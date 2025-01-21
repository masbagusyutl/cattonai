import requests
import json
import time
import datetime
from colorama import Fore, Style, init
from urllib.parse import parse_qs, unquote
from fake_useragent import UserAgent

# Initialize colorama dan UserAgent
init()
ua = UserAgent()

# Constants
BASE_URL = "https://api.catton.tech/api"
CLAN_ID = "63128420"

def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop CattonAi")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop\n")

def print_separator():
    print(Fore.CYAN + "=" * 50)

def format_number(number):
    try:
        return "{:,}".format(float(number))
    except:
        return number

def get_login_headers(auth_data):
    """
    Membuat header untuk login tanpa pseudo-header.
    """
    return {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'auth': auth_data,  # Data autentikasi dari file data.txt
        'authorization': 'Bearer',  # Tetap disertakan, meskipun mungkin kosong untuk login awal
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://play.catton.tech',
        'pragma': 'no-cache',
        'referer': 'https://play.catton.tech/',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge WebView2";v="131"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': ua.random,  
    }

def get_bearer_headers(token):
    """
    Buat header untuk endpoint yang membutuhkan token.
    """
    return {
        'authority': 'api.catton.tech',
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://play.catton.tech',
        'referer': 'https://play.catton.tech/',
        'user-agent': ua.random,
        'authorization': f'Bearer {token}'
    }

def extract_username(auth_data):
    try:
        parsed = parse_qs(auth_data)
        user_data = parsed.get('user', ['{}'])[0]
        user_json = json.loads(unquote(user_data))
        return user_json.get('username', 'unknown')
    except Exception as e:
        print(Fore.RED + f"Error saat mengekstrak username: {str(e)}")
        return 'unknown'

def load_accounts():
    try:
        with open('data.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + "Error: File data.txt tidak ditemukan!")
        return []

def ensure_auth_format(auth_data):
    """
    Memastikan data `auth` memiliki format lengkap, termasuk bagian "::false".
    """
    if not auth_data.endswith("::false"):
        auth_data += "::false"
    return auth_data

def login_account(auth_data):
    """
    Melakukan login ke API menggunakan data autentikasi Telegram.
    """
    # Pastikan format `auth` benar
    auth_data = ensure_auth_format(auth_data)

    try:
        headers = get_login_headers(auth_data)
        username = extract_username(auth_data)
        print(Fore.CYAN + f"👤 Login sebagai: @{username}")

        # Payload login
        payload = {
            "auth": None,  # Sesuai dengan contoh payload dari respons valid
            "invite_id": 0,
            "is_premium": False,
            "avatar_url": None
        }

        # Kirim permintaan POST ke endpoint login
        response = requests.post(f"{BASE_URL}/users/login_tele_tg_data", headers=headers, json=payload)

        if response.status_code == 200:
            # Ambil token dari cookie
            token = response.cookies.get('access_token')
            if not token:
                print(Fore.RED + "❌ Token tidak ditemukan di cookie.")
                return None
            print(Fore.GREEN + "✓ Login berhasil.")
            return token
        else:
            # Tampilkan error jika status code bukan 200
            print(Fore.RED + f"Login gagal: Status Code {response.status_code}")
            print(Fore.YELLOW + f"Respons: {response.text}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat login: {str(e)}")
        return None

def get_user_stats(headers):
    try:
        response = requests.get(f"{BASE_URL}/user-stat", headers=headers)
        if response.status_code == 200:
            stats = response.json()['result']
            print_separator()
            print(Fore.GREEN + "Statistik User:")
            print(Fore.CYAN + f"💰 Gold: {format_number(stats['gold'])}")
            print(Fore.CYAN + f"⭐ EXP: {format_number(stats['exp'])}")
            print(Fore.CYAN + f"💎 Gem: {format_number(stats['gem'])}")
            print(Fore.CYAN + f"🔮 Crystal: {format_number(stats['crystal'])}")
            print(Fore.CYAN + f"Free Mine: {stats['freeMine']}")
            print(Fore.YELLOW + "Equipment:")
            for item in stats.get('items', []):
                print(Fore.CYAN + f"- {item['type']}: Level {item['level']}")
            return stats
        else:
            print(Fore.RED + "Gagal mendapatkan statistik user.")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat mengambil statistik user: {str(e)}")
        return None

def do_mining(headers):
    stats = get_user_stats(headers)
    if not stats or stats['freeMine'] == 0:
        print(Fore.YELLOW + "Tidak ada freeMine yang tersedia. Melewati mining.")
        return False

    try:
        response = requests.post(f"{BASE_URL}/mine/open", headers=headers, json={})
        if response.status_code == 200:
            result = response.json()['result']
            print_separator()
            print(Fore.GREEN + "Hasil Mining:")
            print(Fore.CYAN + f"Reward: {result['slot']['reward']}")
            print(Fore.CYAN + f"Rarity: {result['slot']['rarity']}")
            print(Fore.CYAN + f"Earned: {format_number(result['earned'])}")
            return True
        else:
            print(Fore.RED + f"Gagal melakukan mining: {response.text}")
            return False
    except Exception as e:
        print(Fore.RED + f"Error saat mining: {str(e)}")
        return False

def process_achievements(headers):
    try:
        # Fetch achievements data
        response = requests.get(f"{BASE_URL}/achievement/", headers=headers)
        if response.status_code == 200:
            achievements = response.json().get('result', {}).get('quests', [])
            print_separator()
            print(Fore.GREEN + "Memproses Achievements...")

            for achievement in achievements:
                # Jika state 'Complete', langsung klaim
                if achievement['state'] == 'Complete':
                    claim_response = requests.post(
                        f"{BASE_URL}/achievement/claim",
                        headers=headers,
                        json={"minestone": achievement['minestone']}
                    )

                    if claim_response.status_code == 200:
                        print(Fore.GREEN + f"✓ Achievement Level {achievement['level']} berhasil diklaim.")
                    else:
                        print(Fore.RED + f"✗ Gagal klaim Achievement Level {achievement['level']}.")
                    continue  # Lanjut ke achievement berikutnya

                # Jika state 'Doing', periksa melalui check_partner
                if achievement['state'] == 'Doing':
                    check_response = requests.post(
                        f"{BASE_URL}/achievement/check_partner",
                        headers=headers,
                        json={"minestone": achievement['minestone']}
                    )

                    if check_response.status_code == 200:
                        # Update state setelah check_partner
                        updated_achievement = check_response.json().get('result', {}).get('quests', [])
                        for updated in updated_achievement:
                            if updated['minestone'] == achievement['minestone']:
                                achievement['state'] = updated['state']
                                break

                        # Jika state berubah menjadi 'Complete', klaim
                        if achievement['state'] == 'Complete':
                            claim_response = requests.post(
                                f"{BASE_URL}/achievement/claim",
                                headers=headers,
                                json={"minestone": achievement['minestone']}
                            )

                            if claim_response.status_code == 200:
                                print(Fore.GREEN + f"✓ Achievement Level {achievement['level']} berhasil diklaim.")
                            else:
                                print(Fore.RED + f"✗ Gagal klaim Achievement Level {achievement['level']}.")
                        else:
                            print(Fore.CYAN + f"Achievement Level {achievement['level']} dengan minestone {achievement['minestone']} masih belum bisa diklaim. Melewati.")
                    else:
                        print(Fore.YELLOW + f"⚠️ Gagal memeriksa partner untuk minestone {achievement['minestone']}. Melewati.")
                else:
                    print(Fore.CYAN + f"Achievement Level {achievement['level']} dengan minestone {achievement['minestone']} memiliki state '{achievement['state']}' dan dilewati.")
        else:
            print(Fore.RED + f"Gagal mendapatkan data achievements. Status code: {response.status_code}")
    except Exception as e:
        print(Fore.RED + f"Error saat memproses achievements: {str(e)}")

def process_quests(headers):
    """
    Memproses quests berdasarkan status dari API `/quest/`.
    """
    try:
        # Ambil semua quest dari API `/quest/`
        response = requests.get(f"{BASE_URL}/quest/", headers=headers)
        if response.status_code != 200:
            print(Fore.RED + f"Error: Tidak dapat mengambil data quest. Status Code: {response.status_code}")
            return

        quests_data = response.json().get('result', {})
        social_quests = quests_data.get('socialQuests', [])

        if not social_quests:
            print(Fore.YELLOW + "Tidak ada social quest yang ditemukan.")
            return

        # Urutkan social quests berdasarkan `show_priority`
        social_quests = sorted(social_quests, key=lambda x: x.get('show_priority', float('inf')))

        print_separator()
        print(Fore.GREEN + "Memproses Social Quests...")

        for quest in social_quests:
            quest_id = quest.get('id')
            content = quest.get('content', 'Quest Tidak Diketahui')
            link = quest.get('link', '')
            state = quest.get('state', '')

            print(Fore.CYAN + f"🎯 Memproses quest: '{content}' (ID: {quest_id})")

            # Lewati jika quest sudah "Complete" atau "Claimed"
            if state in ["Complete", "Claimed"]:
                print(Fore.YELLOW + f"⚠️ Quest '{content}' sudah dalam status '{state}'. Melewati.")
                continue

            # Jika quest dalam status "Doing", lakukan check_open_link_social_quest
            if state == "Doing" and link:
                print(Fore.CYAN + f"🔗 Membuka link: {link}")
                check_response = requests.post(
                    f"{BASE_URL}/quest/check_open_link_social_quest/{quest_id}",
                    headers=headers,
                    json={"quest_id": quest_id}
                )
                if check_response.status_code == 200:
                    print(Fore.GREEN + f"✅ Quest '{content}' berhasil diselesaikan.")
                else:
                    print(Fore.RED + f"❌ Gagal menyelesaikan quest '{content}'. Respons: {check_response.text}")
                    continue

            # Setelah check_open_link, lakukan klaim jika status berubah menjadi "Complete"
            claim_response = requests.get(f"{BASE_URL}/quest/", headers=headers)
            updated_quests = claim_response.json().get('result', {}).get('socialQuests', [])
            updated_quest = next((q for q in updated_quests if q['id'] == quest_id), None)

            if updated_quest and updated_quest.get('state') == "Complete":
                print(Fore.CYAN + f"🏆 Klaim reward untuk quest '{content}'...")
                claim_result = requests.post(
                    f"{BASE_URL}/quest/claim_social_quest/{quest_id}",
                    headers=headers,
                    json={}
                )
                if claim_result.status_code == 200:
                    print(Fore.GREEN + f"🎉 Reward untuk quest '{content}' berhasil diklaim.")
                else:
                    print(Fore.RED + f"❌ Gagal klaim reward untuk quest '{content}'. Respons: {claim_result.text}")
            else:
                print(Fore.YELLOW + f"⚠️ Quest '{content}' belum dalam status 'Complete'. Melewati.")

        print(Fore.GREEN + "Semua social quest telah diproses.")
    except Exception as e:
        print(Fore.RED + f"Error saat memproses quests: {str(e)}")

def upgrade_item(headers, item_type, amount=1):
    """
    Melakukan permintaan upgrade untuk item tertentu.

    Parameters:
        headers (dict): Header autentikasi.
        item_type (str): Jenis item yang akan di-upgrade (contoh: "Armor").
        amount (int): Jumlah item untuk di-upgrade. Default adalah 1.
    """
    payload = {"item_type": item_type, "amount": amount}
    try:
        response = requests.post(f"{BASE_URL}/user-stat/upgrade_item", headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result['code'] == 0:
                for item in result['result'].get('items', []):
                    if item['type'] == item_type:
                        print(Fore.GREEN + f"✓ {item_type} berhasil di-upgrade ke Level {item['level']}.")
            elif result['code'] == 20:
                print(Fore.RED + f"✗ Gagal upgrade {item_type}: {result['result']['message']}")
            else:
                print(Fore.RED + f"✗ Gagal upgrade {item_type}: Kode tidak diketahui ({result['code']})")
        else:
            print(Fore.RED + f"✗ Gagal melakukan permintaan upgrade {item_type}. Status Code: {response.status_code}")
    except Exception as e:
        print(Fore.RED + f"Error saat mencoba upgrade {item_type}: {str(e)}")

def active_buff(headers):
    """
    Mengaktifkan buff dan menampilkan daftar buff aktif jika waktunya memungkinkan.

    Parameters:
        headers (dict): Header autentikasi.
    """
    try:
        # Periksa status buff terlebih dahulu
        check_response = requests.get(f"{BASE_URL}/blessing", headers=headers)
        if check_response.status_code == 200:
            check_result = check_response.json()
            if check_result['code'] == 0:
                buff_time = check_result['result']['buffTime'] / 1000
                current_time = datetime.datetime.now().timestamp()

                # Jika belum waktunya, jangan aktifkan buff
                if current_time < buff_time:
                    remaining_time = buff_time - current_time
                    hours, remainder = divmod(remaining_time, 3600)
                    minutes, _ = divmod(remainder, 60)
                    print(Fore.YELLOW + f"⚠️ Buff belum bisa diaktifkan. Tunggu sekitar {int(hours)} jam {int(minutes)} menit lagi.")
                    return
                else:
                    print(Fore.GREEN + "✓ Sudah waktunya untuk mengaktifkan buff.")
            else:
                print(Fore.RED + "✗ Gagal memeriksa status buff.")
                return
        else:
            print(Fore.RED + f"✗ Gagal memeriksa status buff. Status Code: {check_response.status_code}")
            return

        # Jika sudah waktunya, aktifkan buff
        payload = {"pack_id": 1}
        response = requests.post(f"{BASE_URL}/blessing/active_buff", headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result['code'] == 0:
                print(Fore.GREEN + "✓ Buff berhasil diaktifkan.")
                print(Fore.CYAN + "Buff aktif saat ini:")
                buffs = result['result']['buffs']
                for buff in buffs:
                    buff_id = buff['id']
                    updated_at = datetime.datetime.fromtimestamp(buff['updatedAt'] / 1000) if buff['updatedAt'] else "Belum diaktifkan"
                    print(Fore.CYAN + f"- Buff ID {buff_id}: Diaktifkan pada {updated_at}")
            else:
                print(Fore.RED + f"✗ Gagal mengaktifkan buff: {result['result']['message']}")
        else:
            print(Fore.RED + f"✗ Gagal melakukan permintaan active_buff. Status Code: {response.status_code}")
    except Exception as e:
        print(Fore.RED + f"Error saat mencoba mengaktifkan buff: {str(e)}")

def check_and_join_clan(headers):
    """Cek apakah pengguna sudah join clan, jika belum maka akan otomatis join."""
    try:
        response = requests.get(f"{BASE_URL}/clan/info", headers=headers, timeout=10)
        data = response.json()
        
        if data.get("code") == 121:
            print(Fore.YELLOW + "🚨 Anda belum bergabung dalam clan. Bergabung ke clan...")
            try:
                join_response = requests.post(f"{BASE_URL}/clan/join", headers=headers, json={"clanId": CLAN_ID}, timeout=10)
                join_data = join_response.json()
                
                if join_data.get("code") == 0:
                    print(Fore.GREEN + f"✅ Berhasil bergabung dengan clan: {join_data['result']['clanName']}")
                else:
                    print(Fore.RED + "❌ Gagal bergabung dengan clan.")
            except requests.RequestException as e:
                print(Fore.RED + f"⚠️ Terjadi kesalahan saat mencoba join clan: {e}")
        elif data.get("code") == 0:
            print(Fore.GREEN + f"✅ Sudah bergabung dengan clan: {data['result']['name']}")
        else:
            print(Fore.RED + "❌ Gagal mendapatkan informasi clan.")
    except requests.RequestException as e:
        print(Fore.RED + f"⚠️ Terjadi kesalahan saat mengambil info clan: {e}")
        print(Fore.YELLOW + "➡️ Melanjutkan tugas lainnya...")

def get_info_season(headers):
    """
    Mendapatkan informasi season saat ini.
    """
    try:
        response = requests.get(f"{BASE_URL}/clan/boss/season", headers=headers)
        if response.status_code == 200:
            season_data = response.json().get('result', {})
            print(Fore.GREEN + "\n✓ Informasi Season:")
            print(Fore.CYAN + f"Season ID: {season_data['id']}")
            print(Fore.CYAN + f"Mulai: {datetime.datetime.fromtimestamp(season_data['startAt'] / 1000)}")
            print(Fore.CYAN + f"Berakhir: {datetime.datetime.fromtimestamp(season_data['endAt'] / 1000)}")
            return season_data
        else:
            print(Fore.RED + f"Gagal mendapatkan informasi season. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat mendapatkan informasi season: {str(e)}")
        return None

def get_boss_season(headers, season):
    """
    Mendapatkan informasi boss berdasarkan season tertentu.
    """
    try:
        response = requests.get(f"{BASE_URL}/clan/boss", headers=headers, params={"season": season})
        if response.status_code == 200:
            boss_data = response.json().get('result', {})
            print(Fore.GREEN + "\n✓ Informasi Boss:")
            print(Fore.CYAN + f"Boss Attack Level: {boss_data['bossAtkLevel']}")
            print(Fore.CYAN + f"Boss Attack Speed Level: {boss_data['bossAtkSpeedLevel']}")
            print(Fore.CYAN + f"Trait Attack: {boss_data['trait']['atk']}")
            return boss_data
        else:
            print(Fore.RED + f"Gagal mendapatkan informasi boss. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat mendapatkan informasi boss: {str(e)}")
        return None

def boss_battle(headers):
    """
    Melakukan pertarungan dengan boss.
    """
    try:
        response = requests.post(f"{BASE_URL}/clan/boss/battle", headers=headers, json={})
        if response.status_code == 200:
            battle_data = response.json().get('result', {})
            print(Fore.GREEN + "\n✓ Hasil Pertempuran:")
            print(Fore.CYAN + f"Damage Dealt: {battle_data['damageDealt']}")
            print(Fore.CYAN + f"EXP Reward: {battle_data['expReward']}")
            print(Fore.CYAN + "Log Pertempuran:")
            for log in battle_data['result']['actionLogs']:
                print(Fore.YELLOW + f"- Damage: {log['damage']}, Critical: {log['isCrit']}, Dodge: {log['isDodge']}")
            return battle_data
        else:
            print(Fore.RED + f"Gagal melakukan pertempuran. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat melakukan pertempuran: {str(e)}")
        return None

def get_clan_trait(headers):
    """
    Mendapatkan informasi trait clan saat ini.
    """
    try:
        response = requests.get(f"{BASE_URL}/clan/trait", headers=headers)
        if response.status_code == 200:
            trait_data = response.json().get('result', {})
            print(Fore.GREEN + "\n✓ Informasi Trait Clan:")
            print(Fore.CYAN + f"Season: {trait_data['season']}")
            for stat in trait_data['stats']:
                print(Fore.CYAN + f"Type: {stat['type']}, Level: {stat['level']}, Locked: {stat['isLocked']}")
            print(Fore.CYAN + f"Total Attack: {trait_data['atk']}")
            return trait_data
        else:
            print(Fore.RED + f"Gagal mendapatkan informasi trait clan. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat mendapatkan informasi trait clan: {str(e)}")
        return None

def randomize_clan_trait(headers, lock_slot=None):
    """
    Melakukan randomisasi trait clan.

    Parameters:
        lock_slot (str): Slot yang ingin dikunci (jika ada).
    """
    payload = {"lock_slot": lock_slot or ""}
    try:
        response = requests.post(f"{BASE_URL}/clan/randomTrait", headers=headers, json=payload)
        if response.status_code == 200:
            random_trait_data = response.json().get('result', {})
            print(Fore.GREEN + "\n✓ Randomisasi Trait Clan Berhasil:")
            for stat in random_trait_data['stats']:
                print(Fore.CYAN + f"Type: {stat['type']}, Level: {stat['level']}, Locked: {stat['isLocked']}")
            print(Fore.CYAN + f"Total Attack: {random_trait_data['atk']}")
            return random_trait_data
        else:
            print(Fore.RED + f"Gagal melakukan randomisasi trait clan. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat randomisasi trait clan: {str(e)}")
        return None

def get_clan_quests(headers):
    """
    Mendapatkan daftar quest clan saat ini.
    """
    try:
        response = requests.get(f"{BASE_URL}/clan/quest/", headers=headers)
        if response.status_code == 200:
            quests_data = response.json().get('result', {}).get('quests', [])
            return quests_data
        else:
            print(Fore.RED + f"Gagal mendapatkan informasi clan quests. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat mendapatkan informasi clan quests: {str(e)}")
        return None

def claim_clan_quest(headers, quest_id):
    """
    Melakukan klaim pada quest clan tertentu.

    Parameters:
        quest_id (int): ID dari quest yang ingin diklaim.
    """
    try:
        quests = get_clan_quests(headers)
        quest_to_claim = next((quest for quest in quests if quest['id'] == quest_id and quest['state'] == "Complete"), None)

        if not quest_to_claim:
            print(Fore.YELLOW + f"⚠️ Quest ID {quest_id} tidak dapat diklaim karena statusnya belum 'Complete'.")
            return None

        payload = {"quest_id": quest_id}
        response = requests.post(f"{BASE_URL}/clan/quest/claim", headers=headers, json=payload)
        if response.status_code == 200:
            print(Fore.GREEN + f"\n✓ Quest dengan ID {quest_id} berhasil diklaim.")
            return response.json().get('result', {})
        else:
            print(Fore.RED + f"Gagal klaim quest clan. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat klaim quest clan: {str(e)}")
        return None

def get_clan_achievements(headers):
    """
    Mendapatkan daftar pencapaian clan saat ini.
    """
    try:
        response = requests.get(f"{BASE_URL}/clan/achievement/", headers=headers)
        if response.status_code == 200:
            achievements_data = response.json().get('result', {}).get('quests', [])
            return achievements_data
        else:
            print(Fore.RED + f"Gagal mendapatkan informasi clan achievements. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat mendapatkan informasi clan achievements: {str(e)}")
        return None

def claim_clan_achievement(headers, minestone):
    """
    Melakukan klaim pada pencapaian clan tertentu.

    Parameters:
        minestone (int): Minestone dari pencapaian yang ingin diklaim.
    """
    try:
        achievements = get_clan_achievements(headers)
        achievement_to_claim = next((ach for ach in achievements if ach['minestone'] == minestone and ach['state'] == "Complete"), None)

        if not achievement_to_claim:
            print(Fore.YELLOW + f"⚠️ Achievement dengan Minestone {minestone} tidak dapat diklaim karena statusnya belum 'Complete'.")
            return None

        payload = {"minestone": minestone}
        response = requests.post(f"{BASE_URL}/clan/achievement/claim", headers=headers, json=payload)
        if response.status_code == 200:
            print(Fore.GREEN + f"\n✓ Achievement dengan Minestone {minestone} berhasil diklaim.")
            return response.json().get('result', {})
        else:
            print(Fore.RED + f"Gagal klaim achievement clan. Status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error saat klaim achievement clan: {str(e)}")
        return None

def process_boss_events(headers):
    """
    Proses lengkap untuk mendapatkan info season, info boss, dan melakukan pertempuran.
    """
    season_info = get_info_season(headers)
    if not season_info:
        return

    boss_info = get_boss_season(headers, season_info['season'])
    if not boss_info:
        return

    if boss_info['freeTicket'] > 0:
        print(Fore.YELLOW + "\n🎯 Melakukan pertempuran dengan boss...")
        boss_battle(headers)
    else:
        print(Fore.YELLOW + "\n⚠️ Tidak ada tiket gratis untuk pertempuran boss.")

def process_account(token, index, total, username):
    print(Fore.YELLOW + f"\n📱 Memproses akun {index}/{total} [@{username}]")
    headers = get_bearer_headers(token)
    get_user_stats(headers)
    check_and_join_clan(headers)
    process_quests(headers)
    do_mining(headers)
    process_achievements(headers)

    print(Fore.MAGENTA + "\n🔧 Upgrade Item: Armor")
    upgrade_item(headers, "Armor", amount=1)

    print(Fore.MAGENTA + "\n✨ Mengaktifkan Buff")
    active_buff(headers)

    print(Fore.CYAN + "\n🛠️ Memproses Clan Events")
    process_boss_events(headers)

    print(Fore.CYAN + "\n🔄 Randomisasi Clan Trait")
    randomize_clan_trait(headers)

    print(Fore.CYAN + "\n🎯 Memproses Clan Quests")
    quests = get_clan_quests(headers)
    if quests:
        for quest in quests:
            if quest['state'] == "Complete":
                claim_clan_quest(headers, quest['id'])
            else:
                print(Fore.YELLOW + f"⚠️ Quest ID {quest['id']} tidak dapat diklaim karena statusnya belum 'Complete'.")

    print(Fore.CYAN + "\n🏆 Memproses Clan Achievements")
    achievements = get_clan_achievements(headers)
    if achievements:
        for achievement in achievements:
            if achievement['state'] == "Complete":
                claim_clan_achievement(headers, achievement['minestone'])
            else:
                print(Fore.YELLOW + f"⚠️ Achievement dengan Minestone {achievement['minestone']} tidak dapat diklaim karena statusnya belum 'Complete'.")

def main():
    print_welcome_message()
    accounts = load_accounts()
    if not accounts:
        return

    for index, auth_data in enumerate(accounts, 1):
        username = extract_username(auth_data)
        token = login_account(auth_data)
        if token:
            process_account(token, index, len(accounts), username)
        else:
            print(Fore.RED + f"Gagal login untuk @{username}.")
        
        # Menunggu 5 detik sebelum memproses akun berikutnya
        print(Fore.YELLOW + "\n⏳ Menunggu 5 detik sebelum akun berikutnya...")
        time.sleep(5)

    # Semua akun telah diproses
    print(Fore.CYAN + "\n✅ Semua akun telah diproses")
    print(Fore.YELLOW + "⏰ Menunggu 4 jam 48 menit sebelum memulai ulang...\n")
    
    # Penghitung waktu mundur
    end_time = datetime.datetime.now() + datetime.timedelta(days=0.2)
    while datetime.datetime.now() < end_time:
        remaining = end_time - datetime.datetime.now()
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"\r⏳ Waktu tersisa: {hours:02d}:{minutes:02d}:{seconds:02d}", end="")
        time.sleep(1)
    print("\n")

if __name__ == "__main__":
    while True:
        try:
            main()
            print(Fore.CYAN + "🔄 Memulai ulang proses...\n")
        except KeyboardInterrupt:
            print(Fore.RED + "\n⛔ Program dihentikan oleh pengguna")
            break
        except Exception as e:
            print(Fore.RED + f"\n❌ Terjadi error: {str(e)}")
            print("Program akan melanjutkan tugas lainnya...")

