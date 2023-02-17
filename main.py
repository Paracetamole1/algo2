import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

def main():
    brand_entry =input('Entrez votre marque souhaitée : ')
    html_page= requests.get('https://www.lacentrale.fr/listing').text
    soup = BeautifulSoup(html_page, 'html.parser')
    scripts = soup.find_all("script")

    for script in scripts:
        if "window.__PRELOADED_STATE_LISTING__" in script.text:
            bd = script.text.replace('window.__PRELOADED_STATE_LISTING__ = ',"").split(';if(')[0]
            break
        
    data = json.loads(bd)

    array_df = []

    for i in range (len(data['search']['aggs']['vehicle.make'])):
                    
        marques = data['search']['aggs']['vehicle.make'][i]['key']
        if marques.lower()==brand_entry:
            
            for e in range(len(data['search']['aggs']['vehicle.make'][i]['agg'])):
                
                for page in range(1,5):
                    car_modele = data['search']['aggs']['vehicle.make'][i]['agg'][e]['key']
                    url = "https://www.lacentrale.fr/listing?makesModelsCommercialNames="+marques+":"+car_modele+"&page="+str(page)
                    small_soup = BeautifulSoup(requests.get(url).text, 'html.parser')
                    scripts = small_soup.find_all("script")
                    
                    for script in scripts:
                        if "window.__PRELOADED_STATE_LISTING__" in script.text:
                            bd = script.text.replace('window.__PRELOADED_STATE_LISTING__ = ',"").split(';if(')[0]
                            break
                    data = json.loads(bd)
                    if len(data['search']['hits']) == 0:
                        break
                    
                    for car in data['search']['hits']:
                        car = car['item']
                        array_df.append([
                                        marques,
                                        car['vehicle']['model'],
                                        car['vehicle'].get('motorization') or car['vehicle'].get('version'),
                                        car['vehicle']['year'],
                                        car['vehicle']['mileage'],
                                        car['vehicle']['energy'],
                                        car['price']
                                        ])

    try:        
        df_write = pd.DataFrame(array_df)
        df_write.to_csv("helloworld.csv", index=False, header=['brand', 'model', 'motor','year','mileage','fuel','price'])
    except:
        print('Pas de résultats pour cette marque')
main()