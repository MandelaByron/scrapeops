import scrapy
import pandas as pd
from bs4 import BeautifulSoup

import json
from lxml import etree
import json
import os
from inline_requests import inline_requests
from scrapy.http import Request
#path=os.getcwd() + '\\player_links.json'
df=pd.read_json('player_links.json')
# df1 = pd.read_excel(r'C:\Users\HP\Dropbox\PC\Desktop\football\players\links_addons.xlsx')

links= df['link'].values.tolist()
# print(len(links))
#df = pd.read_excel(r'C:\Users\HP\Dropbox\PC\Desktop\football\output-1679181403719 2.xlsx')
# player_links=[]
# for link in df['Player URLs'].values:
#     link = link.replace('marktwertverlauf','profil')
#     player_links.append(link)
#player_links=df['link'].values
base_url='https://www.transfermarkt.co.uk'
class PlayerSpider(scrapy.Spider):
    name = 'player'
    allowed_domains = ['transfermarkt.us','transfermarkt.co.uk']
    start_urls = links
    
    custom_settings = {
        
        'ROBOTSTXT_OBEY': False,
        'FEEDS':{
            'player_data.json':{
                'format':'json',
                'overwrite':True
            }
        }
    }  
    
   # start_urls = ["https://www.transfermarkt.co.uk/lionel-messi/profil/spieler/28003","https://www.transfermarkt.co.uk/aaron-ramsdale/profil/spieler/427568","https://www.transfermarkt.us/donovan-pines/profil/spieler/638692",'https://www.transfermarkt.co.uk/erling-haaland/profil/spieler/418560','https://www.transfermarkt.us/thiago-almada/profil/spieler/576028','https://www.transfermarkt.us/oscar-bobb/profil/spieler/661207','https://www.transfermarkt.co.uk/bukayo-saka/profil/spieler/433177']
    
    # for url in urls:
    #     start_urls.append(url)
    #start_urls=['https://www.transfermarkt.us/louis-blackstock/profil/spieler/935395']
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url , callback=self.parse_player)
    #https://www.transfermarkt.us/ederson/leistungsdaten/spieler/238223
    #https://www.transfermarkt.us/ricardo-pepi/leistungsdatenverein/spieler/627207
    def convert_image_large(self,url):
        return url.replace('tiny','head')
    
    @inline_requests
    def parse_player(self, response):
        base=response.url.split('profil')[0]
        
        profile_id=response.url.split('profil')[1].split('/spieler/')[1]
        
        national_team_stats_url = base + 'nationalmannschaft/spieler/' + profile_id
        
        stats_link = base + 'leistungsdaten/spieler/' + profile_id
        
        current_season_stats_link= base + 'leistungsdatenverein/spieler/' + profile_id
        
        name= response.xpath('//div[@class="data-header__profile-container"]/div/img/@alt').get()
        
        jersey_number=response.xpath('//span[@class="data-header__shirt-number"]/text()').get()
        
        if jersey_number != None:
            jersey_number=jersey_number.strip().replace('#','')
        
        if jersey_number != None:
            jersey_number = int(jersey_number)
        headshot=response.xpath('//div[@class="data-header__profile-container"]/div/img/@src').get()
        if headshot == None:
            headshot = response.xpath('//div[@class="data-header__profile-container"]/img/@src').get()
            name= response.xpath('//div[@class="data-header__profile-container"]/img/@alt').get()

        club = response.xpath('//span[@itemprop="affiliation"]/a/@title').get(default='Retired').strip()
        
        club_logo=response.xpath('//a[@class="data-header__box__club-link"]/img/@srcset').get().strip().replace('\n','').split('1x')[0].strip().replace('normquad','head')
            
        birthday_info = response.xpath('//span[@itemprop="birthDate"]/text()').get()
        if birthday_info != None:

            info=birthday_info.strip().split('(')
            try:
                age=int(info[1].replace(')','').strip())
                dob=info[0].strip()
            except:
                if birthday_info.strip() == '':
                    age=response.xpath('//span[@itemprop="birthDate"]/text()[2]').get().strip().replace('(','').replace(')','')
                    dob=None
                
        else:
            age=None
            dob=None
        #birthday_info = response.xpath('//span[@itemprop="birthDate"]/text()').get(default='').strip()

        
        pob=response.xpath('//span[@itemprop="birthPlace"]/text()').get()
        if pob != None:
            pob=pob.strip()
            if pob == '':
                pob= response.xpath('//span[@class="cp"]/@title').get()
        pob_flag=response.xpath('//ul[@class="data-header__items"][1]/li[2]/img/@src').get()
        
        if pob_flag != None:
            pob_flag=pob_flag.replace('tiny','head')
        # citizen=response.xpath('//span[@itemprop="nationality"]/img/@alt').get()
        # citizen_flag=response.xpath('//span[@itemprop="nationality"]/img/@src').get()
        
        citizen = response.xpath('//span[@class="info-table__content info-table__content--bold"]/img/@alt').getall()
        citizen_flag = response.xpath('//span[@class="info-table__content info-table__content--bold"]/img/@src').getall() 
        
        if len(citizen) == 1:
            citizen = response.xpath('//span[@class="info-table__content info-table__content--bold"]/img/@alt').get()
            citizen_flag = response.xpath('//span[@class="info-table__content info-table__content--bold"]/img/@src').get()
            citizen_flag = citizen_flag.replace('tiny','head')
        elif len(citizen) > 1:
            citizen_flag = [i.replace('tiny','head') for i in citizen_flag]
            
        else:
            pass
            

        
        height=response.xpath('//span[@itemprop="height"]/text()').get()
        if height != None:
            height = height.strip().replace(',','.')
            
        main_position = response.xpath('//ul[@class="data-header__items"][2]/li[2]/span/text()').get()
        if main_position == None:
            main_position = response.xpath('//ul[@class="data-header__items"][2]/li/span/text()').get()
            #main_position = response.xpath('//div[@class="detail-position__box"]/dd/text()').get()
        main_position=main_position.strip()
        
        national_team = response.xpath('//ul[@class="data-header__items"][3]/li[1]/span/a/text()').get()
        if national_team != None:
            national_team=national_team.strip()
            
        national_team_flag = response.xpath('//ul[@class="data-header__items"][3]/li[1]/span/img/@src').get()
        if national_team_flag != None:
            national_team_flag = national_team_flag.replace('tiny','head')
  
        caps=response.xpath('//ul[@class="data-header__items"][3]/li[2]/a[1]/text()').get()
        if caps != None:
            caps=int(caps.strip())
            
        intl_goals=response.xpath('//ul[@class="data-header__items"][3]/li[2]/a[2]/text()').get()
        if intl_goals != None:
            intl_goals = int(intl_goals.strip())
            
        market_value = response.xpath('//div[@class="tm-player-market-value-development__current-value"]/text()').get()
        if market_value != None:
            m_v = market_value.strip()
            if m_v == '':
                market_value = response.xpath('//div[@class="tm-player-market-value-development__current-value"]/a[1]/text()').get()
            market_value = market_value.strip().replace('€','')
            
        other_positions = response.xpath('//div[@class="detail-position__position"]/dl/dd/text()').getall()#list
        if len(other_positions) == 0:
            other_positions = None
        
        league_logo=response.xpath("//a[@class='data-header__league-link']/img/@src").get()
        if league_logo != None:
            league_logo=league_logo.replace('verytiny','header')
        
        league=response.xpath("//a[@class='data-header__league-link']/img/@title").get()
        league_level= response.xpath('//div[@class="data-header__club-info"]/span[@class="data-header__label"][1]/span/text()[2]').get()
        if league_level != None:
            league_level=league_level.strip()
        joined_date=response.xpath('//div[@class="data-header__club-info"]/span[@class="data-header__label"][2]/span/text()').get()
        if joined_date == None:
            joined_date = ''
        if club == 'Without Club':
            joined_date = 'Without club since:' + joined_date
        if club == 'Retired':
            joined_date = 'Retired since: ' + joined_date
        contract_expires=response.xpath('//div[@class="data-header__club-info"]/span[@class="data-header__label"][3]/span/text()').get()
        
        player_agent = response.xpath('//span[@class="info-table__content info-table__content--bold  info-table__content--flex"]/a/text()').get()
        if player_agent == None:
            player_agent = response.xpath('//span[@class="info-table__content info-table__content--bold  info-table__content--flex"]/span/text()').get()
            
            agent_phone = None
            
            agent_email = None
        elif player_agent != None:
            player_agent = player_agent.strip()
            
            player_agent_url=base_url + response.xpath('//span[@class="info-table__content info-table__content--bold  info-table__content--flex"]/a/@href').get()

            agent_resp = yield scrapy.Request(url=player_agent_url)
            
            agent_phone = agent_resp.xpath('//*[@id="main"]/main/header/div[2]/div[2]/div[2]/div[2]/span[2]/text()').get().strip()
            
            agent_email = agent_resp.xpath('//*[@id="main"]/main/header/div[2]/div[2]/div[2]/div[2]/span[6]/text()').get().strip()
        
        ###NATIONAL TEAM STATS
        debut_list =[]
        matches_list = []
        goals_list =[]
        national_teams_list=[]
        teams_flags_list=[]
        age_at_debut_list=[]

        teams = response.xpath('//div[@class="grid national-career__row"]/div[@class="grid__cell grid__cell--club"]/a/text()').getall()
        if len(teams) != 0:
            for i in teams:
                national_teams_list.append(i)
                teams_flags_list.append(national_team_flag)
            target=response.xpath('//div[@class="grid national-career__row"]/div[@class="grid__cell grid__cell--center"][1]').getall()
            matches = response.xpath('//div[@class="grid national-career__row"]/div[@class="grid__cell grid__cell--center"][2]').getall()
            goals = response.xpath('//div[@class="grid national-career__row"]/div[@class="grid__cell grid__cell--center"][3]').getall()
            for ele in target:
                soup = BeautifulSoup(ele,'lxml').get_text().strip()
                debut_list.append(soup)
            for match in matches:
                soup = BeautifulSoup(match,'lxml').get_text().strip()
                if soup == '-':
                    soup = 0
                matches_list.append(int(soup))
            for i in goals:
                soup = BeautifulSoup(i,'lxml').get_text().strip()
                if soup == '-':
                    soup = 0
                goals_list.append(int(soup))
                
            natioanl_team_resp = yield Request(national_team_stats_url)
            
            html = natioanl_team_resp
            rows=html.xpath('//*[@id="main"]/main/div[3]/div[1]/div[1]/table/tbody//td[@class="rechts"]').getall()

            for row in rows:
                soup = BeautifulSoup(row,'lxml')
                
                age_value = soup.text
                
                age_at_debut_list.append(age_value.strip())
            
            
        
        items = {
            'id':profile_id,
            'name':name,
            'age':age,
            'jersey_number':jersey_number,
            'place_of_birth':pob,
            'place_of_birth_flag':pob_flag, 
            'date_of_birth':dob,
            'height':height,
            'citizenship':citizen,
            'citizenship_flag':citizen_flag,
            'headshot':headshot,
            'club':club,
            'club_logo':club_logo,
            'player_agent':player_agent,
            'main_position':main_position,
            'other_postions':other_positions,
            'national_team':national_team,
            'national_team_flag':national_team_flag,
            'caps':caps,
            'international_goals': intl_goals,
            'market_value': market_value,
            'league_name':league,
            'league_level':league_level,
            'league_logo':league_logo,
            'joined_date':joined_date,
            'contract_expires':contract_expires,
            'agency_info':{
                'name':player_agent,
                'agency':player_agent,
                'agent_phone':agent_phone,
                'agent_email':agent_email,
                
            },
            'club_stats': {
                            'club_logos':[],
                            'clubs':[],
                            'appearances':[],
                            'goals':[],
                            'assists':[],
                            'mins':[],

                           },
            'national_team_stats': {
                'teams_flag':teams_flags_list,
                'national_teams':national_teams_list,
                'appearances':matches_list,
                'goals':goals_list,
                'debut':debut_list,
                'age_at_debut':age_at_debut_list
            } ,
            
            'current_seasons_stats': {
                'competions':[],
                'appearances':[],
                'goals':[],
                'assists':[],
                'yellow_cards':[],
                'second_yellow_cards':[],
                'red_cards':[],
                'mins':[],
                'competition_logos':[]
            }
            
            
            
        }
        
        request = scrapy.Request(url=current_season_stats_link,callback=self.parse_player_all_seasons)
        request.cb_kwargs['player_data'] = items
        request.cb_kwargs['stats_url'] = stats_link
        
        yield request
        
    def parse_player_all_seasons(self, response,player_data,stats_url):
        # teams=response.xpath('//div[@class="box"][2]/table/tbody/td[@class="hauptlink no-border-links"]/a/text()').getall()
        # appearances=response.xpath('//div[@class="box"][2]/table/tbody/td[@class="zentriert"]/a/text()').getall()
        #print(stats_url)
        print(response.url,"---parse_all_seasons")
        club_logo_list= response.xpath('//td[@class="hauptlink no-border-rechts zentriert"]/a/img/@src').getall()
        
        club_logo_list = [i.replace('tiny','header') for i in club_logo_list]
        try:
            df=pd.read_html(response.text)
            if (player_data['main_position'] != 'Goalkeeper'):
            
                clubs=df[0]['Club.1'].values.tolist()[:-1] 

                matches=df[0]['Unnamed: 2'].values.tolist()[:-1] 
                
                goals=df[0]['Unnamed: 3'].values.tolist()[:-1] 

                assists=df[0]['Unnamed: 4'].values.tolist()[:-1] 
                
                mins=df[0]['Unnamed: 8'].values.tolist()[:-1] 
                [player_data['club_stats']['clubs'].append(i)for i in clubs]  
                [player_data['club_stats']['appearances'].append(i)for i in matches]   
                [player_data['club_stats']['goals'].append(i)for i in goals]  
                [player_data['club_stats']['assists'].append(i)for i in assists]  
                [player_data['club_stats']['mins'].append(i.replace('.',''))for i in mins] 
                [player_data['club_stats']['club_logos'].append(i)for i in club_logo_list] 
            else:
                clubs=df[0]['Club.1'].values.tolist()[:-1] 
                [player_data['club_stats']['clubs'].append(i)for i in clubs] 
                matches=df[0]['Unnamed: 2'].values.tolist()[:-1] 
                [player_data['club_stats']['appearances'].append(i)for i in matches] 
                goals=df[0]['Unnamed: 3'].values.tolist()[:-1] 
                [player_data['club_stats']['goals'].append(i)for i in goals]
            
        
                ##replace key 'assists' wth 'cleansheets'
                player_data['club_stats']['cleansheets'] = player_data['club_stats'].pop('assists')
            
                player_data['club_stats']['goals_conceded'] = df[0]['Unnamed: 7'].values.tolist()[:-1] 
                
                player_data['club_stats']['cleansheets']=df[0]['Unnamed: 8'].values.tolist()[:-1] 
                
                [player_data['club_stats']['club_logos'].append(i)for i in club_logo_list] 
            request = scrapy.Request(url=stats_url, callback=self.parse)
            request.cb_kwargs['player_data'] = player_data
            yield request 
        except (ValueError, KeyError) as error:
            print('No stats------', error)
            yield player_data

    def parse(self, response , player_data):
        print(response.url,"----parse")
        
        competition_logos = response.xpath('//td[@class="hauptlink no-border-rechts"]/img/@src').getall()
        
        competition_logos = [i.replace('tiny','header') for i in competition_logos]
        try:
            df = pd.read_html(response.text)[1]
            if (player_data['main_position'] != 'Goalkeeper'):
                #clubs=df[0]['Club.1'].values.tolist()[:-1] 
                competions=df['Competition.1'].values.tolist()[:-1]
                
                appearances=df['wettbewerb'].values.tolist()[:-1]
            
                goals = df['Unnamed: 3'].values.tolist()[:-1] 
                
                assists=df['Unnamed: 4'].values.tolist()[:-1]
                
                yellow_cards=df['Unnamed: 5'].values.tolist()[:-1]
                
                second_yellow_cards=df['Unnamed: 6'].values.tolist()[:-1]
                
                red_cards = df['Unnamed: 7'].values.tolist()[:-1]
                
                
                
                mins = df['Unnamed: 8'].values.tolist()[:-1]
                #'current_seasons_stats'
                [player_data['current_seasons_stats']['competions'].append(i)for i in competions]
                [player_data['current_seasons_stats']['appearances'].append(i)for i in appearances]
                [player_data['current_seasons_stats']['goals'].append(i)for i in goals]
                [player_data['current_seasons_stats']['assists'].append(i)for i in assists]
                [player_data['current_seasons_stats']['yellow_cards'].append(i)for i in yellow_cards]
                [player_data['current_seasons_stats']['second_yellow_cards'].append(i)for i in second_yellow_cards]
                [player_data['current_seasons_stats']['red_cards'].append(i)for i in red_cards]
                [player_data['current_seasons_stats']['competition_logos'].append(i) for i in competition_logos]
                [player_data['current_seasons_stats']['mins'].append(i.replace('.','')) for i in mins]

                
            else :

                ##goalkeepers
                competions=df['Competition.1'].values.tolist()[:-1]
                [player_data['current_seasons_stats']['competions'].append(i)for i in competions]
                appearances=df['wettbewerb'].values.tolist()[:-1]
                [player_data['current_seasons_stats']['appearances'].append(i)for i in appearances]
                goals = df['Unnamed: 3'].values.tolist()[:-1]
                [player_data['current_seasons_stats']['goals'].append(i)for i in goals]
                yellow_cards=df['Unnamed: 4'].values.tolist()[:-1]
                [player_data['current_seasons_stats']['yellow_cards'].append(i)for i in yellow_cards]
                second_yellow_cards=df['Unnamed: 5'].values.tolist()[:-1]
                [player_data['current_seasons_stats']['second_yellow_cards'].append(i)for i in second_yellow_cards]
                red_cards=df['Unnamed: 5'].values.tolist()[:-1]
                [player_data['current_seasons_stats']['red_cards'].append(i)for i in red_cards]
                
                mins=df['Unnamed: 9'].values.tolist()
                [player_data['current_seasons_stats']['mins'].append(i.replace('.',''))for i in mins]
                
                goals_conceeded=df['Unnamed: 7'].values.tolist()[:-1]
                player_data['current_seasons_stats']['goals_conceded'] = goals_conceeded
                
                player_data['current_seasons_stats']['cleansheets'] = player_data['current_seasons_stats'].pop('assists')
                player_data['current_seasons_stats']['cleansheets']=df['Unnamed: 8'].values.tolist()[:-1]
            yield player_data
            
        except (ValueError, KeyError) as error:
            print('****no stats****',error)
            yield player_data