# for random passowrd
import string
import secrets
 
 # create url for esi request
def url_creator(character_id, scopes):
    base_url = 'https://esi.evetech.net/latest/characters/'

    # 이거 뒤에 query string 떼내야함
    esi_scopes = {'industry_jobs': '/industry/jobs/?datasource=tranquility'}

    return base_url + str(character_id) + esi_scopes[scopes]
    
def email_creator(character_name):
    domain = '@eveoline.com'
    cut = character_name.split(' ')

    # 이거 이렇게 하지말고 for문 타면서 공백마다! 넣어줘야함
    try:
        cut[1]
        return cut[0] + '!' + cut[1] + domain
    except:
        return cut[0] + domain

def create_random_string():
    alphabet = string.ascii_letters + string.digits
    while True:
        # 알파벳 소문자 5개 이상
        # 알파벳 대문자 5개 이상
        # 숫자 3개 이상
        password = ''.join(secrets.choice(alphabet) for i in range(20))
        if (sum(c.islower() for c in password) >=5
            and sum(c.isupper() for c in password) >= 5
            and sum(c.isdigit() for c in password) >= 3):
            break

    return password