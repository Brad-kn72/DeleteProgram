import winreg
import subprocess
import time
import pyautogui

def uninstall_with_powershell(program_name):
    try:
        print(f"🔍 PowerShell로 {program_name} 설치 여부 확인 중...")
        find_command = f'powershell -Command "Get-WmiObject -Class Win32_Product | Where-Object {{$_.Name -like \'*{program_name}*\'}}"'
        result = subprocess.run(find_command, shell=True, capture_output=True, text=True)

        if program_name.lower() not in result.stdout.lower():
            print(f"❌ {program_name} 은(는) Win32_Product에서 발견되지 않음.")
            return False

        uninstall_command = f'powershell -Command "(Get-WmiObject -Class Win32_Product | Where-Object {{$_.Name -like \'*{program_name}*\'}}).Uninstall()"'
        print(f"🧹 PowerShell로 {program_name} 제거 시도 중...")
        uninstall_result = subprocess.run(uninstall_command, shell=True, capture_output=True, text=True)

        if uninstall_result.returncode == 0:
            print(f"✅ {program_name} 제거 성공 (PowerShell)")
            return True
        else:
            print(f"⚠️ PowerShell로 제거 실패: {uninstall_result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️ PowerShell 제거 중 오류: {e}")
        return False


def uninstall_from_registry(root_key, uninstall_key_path, program_name):
    try:
        with winreg.OpenKey(root_key, uninstall_key_path) as key:
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        if program_name.lower() in display_name.lower():
                            uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                            print(f"🧹 {display_name} 제거 중... 명령어: {uninstall_string}")

                            # 실행
                            process = subprocess.Popen(uninstall_string, shell=True)
                            
                            # GUI 응답 대기 (필요할 때만)
                            if "msiexec" not in uninstall_string.lower():
                                time.sleep(3)
                                pyautogui.press("o")
                            
                            process.wait()
                            print(f"✅ {display_name} 제거 완료 (레지스트리)")
                            return True
                except (FileNotFoundError, PermissionError, OSError):
                    continue
    except Exception as e:
        print(f"⚠️ 레지스트리 탐색 중 오류: {e}")
    return False


def uninstall_program(program_name):
    print(f"🚀 {program_name} 제거 프로세스 시작")

    # PowerShell로 우선 제거 시도
    if uninstall_with_powershell(program_name):
        return

    # 레지스트리 제거 시도
    uninstall_key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
    if uninstall_from_registry(winreg.HKEY_LOCAL_MACHINE, uninstall_key_path, program_name):
        return
    if uninstall_from_registry(winreg.HKEY_CURRENT_USER, uninstall_key_path, program_name):
        return

    print(f"❌ {program_name} 제거 실패: WMIC/레지스트리에서 찾을 수 없음.")
