import json
import requests
import os.path

#552934290

token = "AQAAAAAVrWhGAADLWxroDl49PkmZhBq9kJGdHJQ"
tokenvk = "958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008"
URLvk = "https://api.vk.com/method/"
URLya = "https://cloud-api.yandex.net/v1/disk/resources"
pathdiskya = "IMO"

class YaUploader:
  def __init__(self, token):
    self.token = token

  def get_headers(self):
    return {
      'Content-Type': 'application/json',
      'Authorization': 'OAuth {}'.format(self.token)
    }

  def get_upload_link(self, disk_file_path, file_disk):
    upload_url = f"{URLya}/upload"
    headers = self.get_headers()
    params = {"path": file_disk, "overwrite": "true"}
    response = requests.get(upload_url, headers=headers, params=params)
    return response.json()

  def upload(self, file_path, file_disk: str):
    href = self.get_upload_link(file_path, file_disk).get("href", "")
    response = requests.put(href, data=open(file_path, 'rb'))
    response.raise_for_status()
    if response.status_code == 201:
      print(f" Файл {file_path} загружен в YD")
    else:
      print(f" Ошибка: {response.status_code}")

  def create_folder(self, name_folder: str):
    print(f"Создаем папку {name_folder} в YD...")
    upload_url = URLya
    headers = self.get_headers()
    params = {"path": name_folder}
    response = requests.put(upload_url, headers=headers, params=params)
    if response.status_code == 201:
      print(f"Папка содана")
    if response.status_code == 409:
      print(f"Папка уже существует")

def vkcommand(command, params):
  return requests.get(f"{URLvk}{command}", params=params)

iduser = input("Введите ID пользователя в VK: ")
print(vkcommand('users.get', {'user_ids': iduser, 'access_token': tokenvk, 'v': '5.131'}).json())

uploader = YaUploader(token)
uploader.create_folder(pathdiskya)

resjson = []
js = vkcommand('photos.get', {'owner_id': iduser, 'album_id': 'profile', 'extended': 1, 'access_token': tokenvk, 'v': '5.131'}).json()
print(f"Нашли {js['response']['count']} фото.")
for section in js['response']['items']:
  date = section['date']
  countlike = section['likes']['count']
  sfullfilename = rf"{countlike}.jpg"
  if os.path.exists(sfullfilename):
    sfullfilename = rf"{countlike}_{date}.jpg"
  surl = section['sizes'][-1]['url']
  size = section['sizes'][-1]['type']
  print(f"Скачиваем файл из VK с id={section['id']} лайки={countlike}, размер={size}")
  f = open(sfullfilename, "wb")
  ufr = requests.get(surl)
  f.write(ufr.content)
  f.close()
  print(f" Закачиваем файл {sfullfilename} в YD...")
  uploader.upload(sfullfilename, f"disk:/{pathdiskya}/{sfullfilename}")
  print(f" Удалям локальную копию.")
  os.remove(sfullfilename)
  resjson.append({"file_name": "'+sfullfilename+'","size": "'+size+'"})

with open('requiremеnts.txt', 'w') as outfile:
  json.dump(resjson, outfile)

print(f"Закачиваем файл requiremеnts.txt в YD...")
uploader.upload('requiremеnts.txt', f"disk:/{pathdiskya}/requiremеnts.txt")
