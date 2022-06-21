import advertools as adv
import pandas as pd
import streamlit as st
import os

st.set_page_config(layout='wide')
st.title('URL Crawler')

url_ = st.text_input('URL', 'https://baxter-factory.fr/')                         #, 'https://baxter-factory.fr/'
advanced = st.checkbox('Advanced Search')
#to = st.number_input('Crawl Timeout',1,60,30)
depth = st.slider('Depth limit',1,10,2)
sch = st.button('Search')



output_file='my_output_file_3.jl'
def filedel(output_file):
    if (os.path.exists(output_file)==True):                                             #supprime output_file existant
        print(output_file+' file exists, deleting...')
        os.remove(output_file)
    else:
        print('creating '+output_file+' file...')

filedel(output_file)

adv.crawl(url_, output_file, follow_links=True, custom_settings={'DEPTH_LIMIT':depth,'ROBOTSTXT_OBEY': False})
crawl_df = pd.read_json(output_file, lines=True)
#crawl_df[['url','title','meta_desc','h1','h2','h3']]                               #affichage des balises en détail
Lurl=crawl_df.url.tolist()

#print(crawl_df.head())
#print(crawl_df.columns)


def check_tag_usage(crawl_df):
    #TITRE
    n_title = crawl_df["title"].isna().value_counts()                               #recherche de titres manquants
    n_title_perc = crawl_df["title"].isna().value_counts(normalize = True)*100      #% de titres manquants
    title_length = (crawl_df['title'].str.len() > 60).value_counts()                #nb de titres avec +60 caractères
    title_length_perc = (crawl_df['title'].str.len() > 60).value_counts(normalize = True)*100
    title_avg = crawl_df['title'].str.len().mean()                                  #moyenne de caractères

    #DESCRITPION
    n_meta_desc = crawl_df["meta_desc"].isna().value_counts()
    n_meta_desc_perc = crawl_df["meta_desc"].isna().value_counts(normalize = True)*100
    meta_desc_long = (crawl_df['meta_desc'].str.len() > 160).value_counts()
    desc_long_perc = (crawl_df['meta_desc'].str.len() > 160).value_counts(normalize=True) * 100
    meta_desc_short = (crawl_df['meta_desc'].str.len() < 50).value_counts()
    desc_short_perc = (crawl_df['meta_desc'].str.len() < 50).value_counts(normalize=True) * 100
    desc_avg = crawl_df['meta_desc'].str.len().mean()

    #H1
    try :
        n_h1 = crawl_df["h1"].isna().value_counts()
        n_h1_perc = crawl_df["h1"].isna().value_counts(normalize = True)*100
    except KeyError:
        pass

    #H2
    n_h2 = crawl_df["h2"].isna().value_counts()
    n_h2_perc = crawl_df["h2"].isna().value_counts(normalize=True) * 100

    #H3
    try :
        n_h3 = crawl_df["h3"].isna().value_counts()
        n_h3_perc = crawl_df["h3"].isna().value_counts(normalize=True) * 100
    except KeyError:
        pass

    #DATAFRAME
    pd.set_option("display.max_columns", 16)                                        #nb de colonnes afichées
    tag_usage_df = pd.DataFrame(data={'title':n_title,                              #tableau de données
                                      '% title':n_title_perc,
                                      'title length >60':title_length,
                                      '% title length':title_length_perc,
                                      'meta_desc':n_meta_desc,
                                      '% description':n_meta_desc_perc,
                                      'desc >160':meta_desc_long,
                                      '% desc >160':desc_long_perc,
                                      'desc <50':meta_desc_short,
                                      '% desc <50':desc_short_perc,
                                      'h1':n_h1,
                                      '% h1':n_h1_perc,
                                      'h2': n_h2,
                                      '% h2': n_h2_perc,
                                      'h3': n_h3,
                                      '% h3': n_h3_perc})

    #VALUES
    st.write('title average length : ', round(title_avg,1))                       #nb de caractères en moyenne de title et desc
    st.write('description average length : ', round(desc_avg,1))



    def cellvalue(df, x, y):
        a = df.iloc[x][y]                                               # coordonnées de la cellule
        try:
            return (a)
        except ValueError:                                                        # pour les cellules NaN/vides
            return ('0')
        return (a)


    def alert(df,s,x,y):                                                           #fonction d'affichage de problemes de balises
        if (cellvalue(df,x,y)>1):
            st.write(round(cellvalue(df,x,y)),s,y)
        else:
            return(0)

                                                                                    #liste des urls posant problème
    url_list = []
    issue = []

    Lmissing = ['title', 'meta_desc', 'h1', 'h2', 'h3']                             #automatisation des alertes
    for i in Lmissing:
        alert(tag_usage_df,'missing', 1, i)
        issue.append('missing ' + i)
        no_i = crawl_df[crawl_df[i].isna()].url.tolist()
        url_list.append(no_i)


    Llong = ['title length >60','desc >160']
    for i in Llong:
        alert(tag_usage_df,'long', 1, i)
        issue.append('long ' + i)
        if (i == 'title length >60'):
            url_longtitle = crawl_df[crawl_df['title'].str.len() > 60].url.tolist()
            url_list.append(url_longtitle)
        else:
            url_longdesc = crawl_df[crawl_df['meta_desc'].str.len() > 60].url.tolist()
            url_list.append(url_longdesc)


    alert(tag_usage_df, 'short', 1, 'desc <50')
    issue.append('short desc <50')
    url_shorttitle = crawl_df[crawl_df['meta_desc'].str.len() < 50].url.tolist()
    url_list.append(url_shorttitle)


                                                                #creation d'un dictionnaire et son df
    dict1 = {issue[0]:url_list[0],
             issue[1]:url_list[1],
             issue[2]:url_list[2],
             issue[3]:url_list[3],
             issue[4]:url_list[4],
             issue[5]:url_list[5],
             issue[6]:url_list[6],
             issue[7]:url_list[7]}
    #for i in len(issue):
     #   d = {issue[i]:url_list[i]}
      #  dict1.update(d)

    def dict_df(dict):
        df = pd.DataFrame.from_dict(dict, orient='index').transpose()
        return (df)

    def list_url_unique(list_url):
        """donne une liste d'url unique à partir de tous les URL à problème identifiés"""
        list_res = []
        l = len(list_url)
        for i in range(l):
            l2 = len(list_url[i])
            for j in range(l2):
                list_res.append(list_url[i][j])

        return list(set(list_res))

    def get_dict2(mydict, list_url_unique):
        """ retraite le tableau des balise en 0 ou 1 en fonction des url"""

        dict2 = {}
        for k, v in mydict.items():
            list_temp = []
            for y in list_url_unique:
                if y in v:
                    list_temp.append(1)
                else:
                    list_temp.append(0)
            dict2[k] = list_temp
        return dict2

    def get_pd(mydict, url):
        """Obtention du tableau final"""
        step1 = list_url_unique(url)
        step2 = get_dict2(mydict, step1)
        res = pd.DataFrame.from_dict(step2)
        res.index = step1
        return res

    def color_background(dataf):
        """mise en forme du tableau"""

        return dataf.style.applymap(lambda x: "background-color:red; color:red;border:2px solid dodgerblack;" \
            if x == 1 else "background-color:green; color:green;border:2px solid dodgerblack;")

    st.write('DATAFRAME :')
    st.write(tag_usage_df)
    df = get_pd(dict1,url_list)

    s = df.style.set_table_styles([
        {
            "selector": "thead",
            "props": [("background-color", "orange"), ("color", "green"),
                      ("border", "3px solid black"),
                      ("font-size", "2rem"), ("font-style", "italic")]

        },
        {
            "selector": "th.row_heading",
            "props": [("background-color", "orange"), ("color", "green"),
                      ("border", "3px solid black"),
                      ("font-size", "2rem"), ("font-style", "italic")]
        },
    ]).applymap(lambda
                    x: "background-color:red; color:red;border:2px solid dodgerblue;" if x == 1 else "background-color:green; color:green;border:2px solid dodgerblue;")

    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    csv = convert_df(df)

    st.download_button(
        label="Download DF as CSV",
        data=csv,
        file_name='URL_crawl.csv',
        mime='text/csv',
    )

    return(s)



if (sch==True):                                                                      #affichage df au click du bouton
    st.dataframe(check_tag_usage(crawl_df))


#incorporer recherche avancée dans la recherche normale

#voir NOTES iphone

#matplotlib plotly tableau ^^^^


#faire colonne score d'url avec la somme des 0 et 1, mettre des % ou des coleurs et trier dans la DF
#catégoriser les url, faire somme des 0 et 1 par critères et proportioner avec nb d'url dans la caté



#streamlit run C:\Users\imads\Desktop\SEOproject\def5.py

#-------- TO_DO code : indexation, conditions(url : contient, commence par, finit par, etc...)

#-------- ajouter pycharm sur laptop
