import requests
import json
import urllib.request
import csv
import sys, time, threading #for the spinner
import pathlib
import datetime
import pandas as pd

class Spinner:
    busy = False
    delay = 0.1
    
    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor
            
    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay
        
    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()
            
    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()
        
    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False


def get_card_name():

    _name = input("Enter card name: ")
    _price = 0

    scryfall_api_url_base = 'https://api.scryfall.com/cards/named?fuzzy='
    scryfall_api_url_full = scryfall_api_url_base + _name
    response = requests.get(scryfall_api_url_full)
    response_json = response.json()
    json_type = type(response_json)

    with open("data\mtg_prices.txt", "w", encoding='utf-8') as f:
        json.dump(response_json, f, ensure_ascii=False, indent=4)
           
    print(response_json['prices'])


def get_all_card_prices():
    
    _date_column_exists = False
    # Wait while the user types a correct input.
    """
    while True:
        _data_type = input("Enter data type required (oracle, unique, default, all, rulings): ")
        if _data_type.lower() not in ('oracle', 'unique', 'default', 'all', 'rulings'):
            print("Please input an appropriate value.")
        else:
            break
            
    if _data_type == 'oracle':
        _data_type_id = '27bf3214-1271-490b-bdfe-c0be6c23d02e'
    elif _data_type == 'unique':
        _data_type_id = '6bbcf976-6369-4401-88fc-3a9e4984c305'
    elif _data_type == 'default':
        _data_type_id = 'e2ef41e3-5778-4bc2-af3f-78eca4dd9c23'
    elif _data_type == 'all':
        _data_type_id = '922288cb-4bef-45e1-bb30-0c2bd3d3534f'
    elif _data_type == 'rulings':
        _data_type_id = '06f54c0b-ab9c-452d-b35a-8297db5eb940'
    else:
        _data_type_id = null
    """   
    _data_type_id = 'e2ef41e3-5778-4bc2-af3f-78eca4dd9c23'    
    scryfall_all_card_url_base = 'https://api.scryfall.com/bulk-data/'
    scryfall_all_card_url_full = scryfall_all_card_url_base + _data_type_id
    
    response = requests.get(scryfall_all_card_url_full)
    response_json = response.json()
    
    _download_url = response_json['download_uri']
    
    print('\n' + _download_url + '\n')
    
    with Spinner():
            
        final_csv = pathlib.Path('data\card_names.csv')
        original_csv = pathlib.Path('data\original_names.csv')
        
        sys.stdout.write('\b')
        
        # Check whether the CSV exists. If it does, no point recreating
        if final_csv.exists() == False:
            print('No file in directory, creating one.')
            with open(final_csv, mode='w') as card_file:
                card_writer = csv.writer(card_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                
                card_writer.writerow(['Name', 'Set', '\t' + str(datetime.date.today())])
            
            print('Created CSV\n')
        else:
        
            df = pd.read_csv(final_csv)
            
            for columns in df.columns:
                # The tab is needed or else excel changes the date format
                temp_string = '\t' + str(datetime.date.today())
                #print(columns)
                #print(datetime.date.today().strftime("%d/%m/%Y"))
                if (columns == temp_string):
                    print('Column exists\n')
                    _date_column_exists = True
                    break
                       
            if (not _date_column_exists):
                df['\t' + str(datetime.date.today())] = ""
                df.to_csv(final_csv, index=False)
                
            print('CSV already exists\n')
            
        # Check when the file was created.
        #mtime = datetime.datetime.fromtimestamp(final_csv.stat().st_mtime)
        #if (mtime.date() == datetime.date.today()):
        #    print('mtime is the same as today')
      
        # Download the latest list of cards from Scryfall.
        with urllib.request.urlopen(_download_url) as downloaded:
            _list_data = json.loads(downloaded.read().decode())
          
        sys.stdout.write('\b')
        print('Downloaded Data\n')
        
    _name = 'name'
    _set = 'set_name'
    _price = 'prices'
    _currency = 'eur'
    _exists = False
    
    # Read the original CSV (card/set) to retrieve prices for.
    original_df = pd.read_csv(original_csv)
    original_name_list = original_df.values.tolist()
    
    # Read the final csv to see what is already in there.
    final_df = pd.read_csv(final_csv)
    card_name_list = final_df.values.tolist()
    column_name_list = final_df.columns.values.tolist()
    final_list = [column_name_list] + card_name_list

    if (1):
        with Spinner():
            for scryfall_card in _list_data:
                for key_val in scryfall_card:
                    if _name in scryfall_card:
                        
                        for original_list_card in original_name_list:
                            
                            # Match the original names to the downloaded data from scryfall.
                            if (original_list_card[0].lower() == scryfall_card[_name].lower()) and (original_list_card[1].lower() == scryfall_card[_set].lower()):
                                #sys.stdout.write('\b')

                                if (scryfall_card[_price][_currency] == None):
                                    temp_price = '-'
                                else:
                                    temp_price = scryfall_card[_price][_currency]
                                
                                #if not card_name_list:
                                #    print('list is empty')
                                #    card_name_list.append([scryfall_card[_name], scryfall_card[_set], temp_price])
                                #    break
                                    
                                for card in card_name_list:
                                    if card[0].lower() == scryfall_card[_name].lower():
                                        # The card already exists in the final csv. 
                                        # Just add the new price to the last column.
                                        card[-1] = temp_price
                                        _exists = True
                                        print('card exists')
                                        break
                                        
                                if (not _exists):
                                    # The card doesn't exist so create new row.
                                    # The price of the card needs to be added to the last column again.
                                    #for index in range(0, len(column_name_list), 3):
                                       
                                    card_name_list.append([scryfall_card[_name], scryfall_card[_set]])
                                    card[len(column_name_list)-1] = temp_price
                                    
                                    print('add new card')
                                    
                                    break 
                            #else:
                                #print('original_card and scryfall_card dont match')
                        
                        _exists = False
                        break
            #print(final_list)
            
            final_list = [column_name_list] + card_name_list
            final_df = pd.DataFrame(final_list)
            final_df.to_csv(final_csv, index=False, header=None)
        print('Done')
    
get_all_card_prices()

