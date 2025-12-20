#!/usr/bin/env python3
"""
Skrypt do tworzenia GitHub issues na podstawie user stories z pliku user_stories.md
"""
import os
import re
import requests
import sys
import argparse
from typing import List, Dict

# Konfiguracja
REPO_OWNER = "marcin119a"
REPO_NAME = "project_tools"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"


def get_github_token() -> str:
    """Pobiera token GitHub ze zmiennej środowiskowej"""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("Błąd: Nie znaleziono tokenu GitHub.")
        print("Ustaw zmienną środowiskową GITHUB_TOKEN lub GH_TOKEN")
        print("Możesz utworzyć token na: https://github.com/settings/tokens")
        sys.exit(1)
    return token


def parse_user_stories(file_path: str) -> List[Dict]:
    """Parsuje plik user_stories.md i zwraca listę słowników z user stories"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stories = []
    # Dzielimy na sekcje (każda zaczyna się od ##)
    sections = re.split(r'^##\s+\d+\.\s+', content, flags=re.MULTILINE)
    
    for section in sections[1:]:  # Pomijamy pierwszy element (nagłówek)
        lines = section.strip().split('\n')
        if not lines:
            continue
        
        # Tytuł to pierwsza linia
        title = lines[0].strip()
        
        # Szukamy sekcji "Jako", "Chcę", "Aby"
        jako = ""
        chce = ""
        aby = ""
        akceptacja = []
        dane_wejściowe = []
        parametry = []
        
        current_section = None
        body_lines = []
        
        for i, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("**Jako**"):
                jako = line.replace("**Jako**", "").strip()
            elif line.startswith("**Chcę**"):
                chce = line.replace("**Chcę**", "").strip()
            elif line.startswith("**Aby**"):
                aby = line.replace("**Aby**", "").strip()
            elif line == "**Akceptacja:**":
                current_section = "akceptacja"
            elif line == "**Dane wejściowe:**":
                current_section = "dane_wejściowe"
            elif line == "**Parametry:**":
                current_section = "parametry"
            elif line.startswith("- "):
                if current_section == "akceptacja":
                    akceptacja.append(line[2:])
                elif current_section == "dane_wejściowe":
                    dane_wejściowe.append(line[2:])
                elif current_section == "parametry":
                    parametry.append(line[2:])
            elif not line.startswith("---"):
                body_lines.append(line)
        
        # Budujemy body issue
        body_parts = []
        if jako or chce or aby:
            body_parts.append("## Opis")
            if jako:
                body_parts.append(f"**Jako** {jako}")
            if chce:
                body_parts.append(f"**Chcę** {chce}")
            if aby:
                body_parts.append(f"**Aby** {aby}")
            body_parts.append("")
        
        if akceptacja:
            body_parts.append("## Akceptacja")
            for item in akceptacja:
                body_parts.append(f"- {item}")
            body_parts.append("")
        
        if dane_wejściowe:
            body_parts.append("## Dane wejściowe")
            for item in dane_wejściowe:
                body_parts.append(f"- {item}")
            body_parts.append("")
        
        if parametry:
            body_parts.append("## Parametry")
            for item in parametry:
                body_parts.append(f"- {item}")
            body_parts.append("")
        
        body = "\n".join(body_parts)
        
        stories.append({
            "title": title,
            "body": body
        })
    
    return stories


def verify_repo_access(token: str) -> bool:
    """Sprawdza czy mamy dostęp do repozytorium"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    repo_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        repo_data = response.json()
        is_private = repo_data.get("private", False)
        if is_private:
            print(f"✓ Repozytorium jest prywatne - dostęp potwierdzony")
        else:
            print(f"✓ Repozytorium jest publiczne - dostęp potwierdzony")
        return True
    elif response.status_code == 401:
        print("Błąd: Nieprawidłowy token GitHub lub token wygasł.")
        print("Sprawdź czy token ma uprawnienia 'repo'")
        print("Utwórz nowy token na: https://github.com/settings/tokens")
        return False
    elif response.status_code == 404:
        print(f"Błąd: Repozytorium {REPO_OWNER}/{REPO_NAME} nie istnieje lub nie masz do niego dostępu.")
        print("\nMożliwe przyczyny:")
        print("1. Repozytorium jest prywatne i token nie ma uprawnień 'repo'")
        print("2. Repozytorium nie istnieje")
        print("3. Nieprawidłowa nazwa właściciela lub repozytorium")
        print("\nSpróbuj utworzyć token z pełnymi uprawnieniami 'repo' na:")
        print("https://github.com/settings/tokens")
        return False
    else:
        print(f"Błąd przy sprawdzaniu dostępu: {response.status_code}")
        error_data = response.json() if response.text else {}
        error_msg = error_data.get("message", response.text)
        print(f"Wiadomość: {error_msg}")
        return False


def check_issues_enabled(token: str) -> bool:
    """Sprawdza czy issues są włączone w repozytorium"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    repo_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        repo_data = response.json()
        has_issues = repo_data.get("has_issues", False)
        return has_issues
    return False


def check_token_permissions(token: str) -> Dict:
    """Sprawdza uprawnienia tokenu"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Sprawdzamy uprawnienia przez próbę utworzenia testowego issue
    test_data = {
        "title": "TEST - można usunąć",
        "body": "To jest test uprawnień. Możesz to usunąć."
    }
    
    response = requests.post(GITHUB_API_URL, json=test_data, headers=headers)
    
    if response.status_code == 201:
        # Usuwamy testowe issue
        issue_data = response.json()
        issue_number = issue_data.get("number")
        delete_url = f"{GITHUB_API_URL}/{issue_number}"
        requests.patch(delete_url, json={"state": "closed"}, headers=headers)
        return {"can_create": True, "message": "Token ma uprawnienia do tworzenia issues"}
    elif response.status_code == 403:
        error_data = response.json() if response.text else {}
        return {"can_create": False, "message": error_data.get("message", "Brak uprawnień")}
    else:
        return {"can_create": False, "message": f"Nieoczekiwany błąd: {response.status_code}"}


def create_issue(token: str, title: str, body: str) -> Dict:
    """Tworzy issue na GitHubie"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Najpierw próbujemy bez etykiet (mogą nie istnieć w repozytorium)
    data = {
        "title": title,
        "body": body
    }
    
    response = requests.post(GITHUB_API_URL, json=data, headers=headers)
    
    # Jeśli się udało, próbujemy dodać etykiety
    if response.status_code == 201:
        issue_data = response.json()
        issue_number = issue_data.get("number")
        
        # Próbujemy dodać etykiety (jeśli nie istnieją, po prostu je pomijamy)
        labels_url = f"{GITHUB_API_URL}/{issue_number}/labels"
        labels_data = {"labels": ["user-story", "enhancement"]}
        labels_response = requests.post(labels_url, json=labels_data, headers=headers)
        
        # Nie traktujemy błędu z etykietami jako krytyczny
        if labels_response.status_code not in [200, 201]:
            print(f"  ⚠️  Uwaga: Nie udało się dodać etykiet (może nie istnieją w repozytorium)")
        
        return issue_data
    elif response.status_code == 403:
        print(f"Błąd 403: Brak uprawnień do tworzenia issues")
        error_data = response.json() if response.text else {}
        error_msg = error_data.get("message", response.text)
        print(f"Wiadomość: {error_msg}")
        print("\n💡 Rozwiązanie:")
        print("1. Jeśli używasz Fine-grained token:")
        print("   - Przejdź do: https://github.com/settings/tokens")
        print("   - Edytuj swój token")
        print("   - W sekcji 'Repository permissions' -> 'Issues' wybierz 'Read and write'")
        print("   - Zapisz zmiany")
        print("\n2. Jeśli używasz Classic token:")
        print("   - Utwórz nowy token na: https://github.com/settings/tokens")
        print("   - Wybierz 'Generate new token (classic)'")
        print("   - Zaznacz scope: 'repo' (pełny dostęp)")
        print("   - Token musi mieć uprawnienia do issues")
        print("\n3. Sprawdź czy issues są włączone w repozytorium:")
        print(f"   https://github.com/{REPO_OWNER}/{REPO_NAME}/settings")
        return None
    else:
        print(f"Błąd przy tworzeniu issue '{title}': {response.status_code}")
        error_data = response.json() if response.text else {}
        error_msg = error_data.get("message", response.text)
        print(f"Wiadomość: {error_msg}")
        if "documentation_url" in error_data:
            print(f"Więcej informacji: {error_data['documentation_url']}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Tworzy GitHub issues z user stories")
    parser.add_argument(
        "file",
        nargs="?",
        default="user_stories.md",
        help="Plik z user stories (domyślnie: user_stories.md)"
    )
    args = parser.parse_args()
    
    token = get_github_token()
    stories_file = args.file
    
    if not os.path.exists(stories_file):
        print(f"Błąd: Nie znaleziono pliku {stories_file}")
        sys.exit(1)
    
    print(f"Sprawdzanie dostępu do repozytorium {REPO_OWNER}/{REPO_NAME}...")
    if not verify_repo_access(token):
        print("\n💡 Wskazówka: Jeśli repozytorium jest prywatne, upewnij się że:")
        print("   - Token ma uprawnienia 'repo' (pełny dostęp do repozytoriów)")
        print("   - Token nie wygasł")
        print("   - Masz dostęp do repozytorium")
        sys.exit(1)
    
    print("Sprawdzanie czy issues są włączone...")
    if not check_issues_enabled(token):
        print("⚠️  Issues są wyłączone w tym repozytorium!")
        print(f"Włącz issues w ustawieniach: https://github.com/{REPO_OWNER}/{REPO_NAME}/settings")
        print("Settings -> General -> Features -> Issues")
        sys.exit(1)
    print("✓ Issues są włączone")
    
    print("Sprawdzanie uprawnień tokenu do tworzenia issues...")
    perm_check = check_token_permissions(token)
    if not perm_check["can_create"]:
        print(f"❌ {perm_check['message']}")
        print("\n💡 Token nie ma uprawnień do tworzenia issues!")
        print("Rozwiązanie:")
        print("1. Jeśli używasz Fine-grained token:")
        print("   - Przejdź do: https://github.com/settings/tokens")
        print("   - Edytuj swój token")
        print("   - W sekcji 'Repository permissions' -> 'Issues' wybierz 'Read and write'")
        print("   - Zapisz zmiany i użyj nowego tokenu")
        print("\n2. Jeśli używasz Classic token:")
        print("   - Utwórz nowy token: https://github.com/settings/tokens")
        print("   - Wybierz 'Generate new token (classic)'")
        print("   - Zaznacz scope: 'repo' (pełny dostęp)")
        print("   - Skopiuj token i ustaw: export GITHUB_TOKEN='twój_token'")
        sys.exit(1)
    print("✓ Token ma uprawnienia do tworzenia issues\n")
    
    print(f"Parsowanie pliku {stories_file}...")
    stories = parse_user_stories(stories_file)
    
    print(f"Znaleziono {len(stories)} user stories")
    print(f"Tworzenie issues w repozytorium {REPO_OWNER}/{REPO_NAME}...\n")
    
    created = 0
    failed = 0
    
    for i, story in enumerate(stories, 1):
        print(f"[{i}/{len(stories)}] Tworzenie issue: {story['title']}")
        result = create_issue(token, story['title'], story['body'])
        
        if result:
            print(f"  ✓ Utworzono: {result['html_url']}")
            created += 1
        else:
            print(f"  ✗ Nie udało się utworzyć issue")
            failed += 1
        print()
    
    print(f"\nPodsumowanie:")
    print(f"  Utworzono: {created}")
    print(f"  Niepowodzeń: {failed}")


if __name__ == "__main__":
    main()