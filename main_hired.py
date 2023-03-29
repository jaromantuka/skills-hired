import streamlit as st
import pandas as pd
import numpy as np 
from collections import Counter
import plotly.express as px
import math

def wide(): 
    st.set_page_config(layout="wide")
wide()


header = st.container()
data_and_selection = st.container()
graphs = st.container()
hist = st.container()

@st.cache
def get_data(filename):
    data = pd.read_csv(filename)
    return data
    
#header in Ukr.
with header: 

    st.title('Salary and Skills of Hired Candidates') #Most Popular Skills Among
    st.markdown('We analyzed data from the profiles of **12K candidates** who were hired on Djinni since March 2022. \
         Select a category and experience below to see the key skills and salaries these candidates have listed in their profiles.' )

with data_and_selection: 
    st.subheader('Choose the category and experience')
#loading data
    cand = get_data('skills_hired_cand.csv')
    cand = cand.dropna()
    cand.rename(columns = {'skills_cache':'all_skils'}, inplace=True)

    cat_col, exp_col = st.columns(2, gap = 'medium')

 #the dropdown. value = '' (defealt)
    options = cand['primary_keyword'].unique()
    options = np.insert(options,0,'')
    options = np.sort(options)
    keyword = cat_col.selectbox('Empty choice shows all the categories together', options = options, index =0) 

#experience range
    m = float(cand.experience_years.min())
    x = float(cand.experience_years.max())

    exp_range = exp_col.slider('Here you can narrow the experience of hired candidates', value = [m,x], step = 0.5)
    
# the function takes data and category and returns a list of skills in category in order of popularity 
    def one_list(data, keyword='', exp=exp_range):
        a = data[(data.experience_years <= exp[1]) & (data.experience_years >= exp[0])]
        if keyword: 
            a = a[a['primary_keyword'] == keyword]
        
        skils = a['all_skils']
        list = skils.tolist()
        all_skils = []
        for i in range(len(list)):
            a = list[i]
            a = a.split('\n')
            all_skils.append(a)
        flat_listt = [item for sublist in all_skils for item in sublist]
        flat_list =[]
        for skill in flat_listt: 
            skill = skill.strip()
            if skill != keyword:
                flat_list.append(skill)
        myDict = Counter(flat_list)

        skillshare = pd.DataFrame.from_dict(myDict, orient='index')
        skillshare['skill'] = skillshare.index
        skillshare.rename(columns = {0:'count'}, inplace=True)
        skillshare = skillshare[['skill', 'count']]
        skillshare = skillshare.reset_index(drop=True)
        skillshare = skillshare.sort_values(by='count', ascending=False).head(15)
        skillshare = skillshare.sort_values(by='count', ascending=True)
        
        return skillshare

with graphs:

    if keyword == '':
        filted = cand[(cand.experience_years <=exp_range[1]) & (cand.experience_years >=exp_range[0])]
        
    else:
        filted = cand[(cand['primary_keyword'] == keyword)&(cand.experience_years <=exp_range[1]) & (cand.experience_years >=exp_range[0])]
    
    #execute the function to know the skills
    cand_skills = one_list(cand, keyword = keyword, exp =exp_range)
    
    top = cand_skills.sort_values(by='count', ascending=False).head(1).reset_index()


    st.subheader('{} is the most popular skills among hired {} candidates'.format(top.skill[0], keyword))

    num_cand = filted.shape[0]
    st.markdown('Candidates in selection: {}'.format(num_cand))
    

    fig = px.bar(cand_skills, x="count", y="skill", orientation='h', labels={"skill": "Top Skills", 'count':'Candidates with the skill'},)

    fig.update_yaxes(tickfont=dict(size=12))
    fig.update_xaxes(tickfont=dict(size=10))
    fig.update_layout(height=5000)

    st.plotly_chart(fig)
    
with hist:
    med = filted['salary_min'].median()
    filted = filted[filted['salary_min']<=17000]
    st.subheader('{} is the median salary among hired {} candidates with {} - {} years of experience'\
                 .format(med, keyword, exp_range[0],exp_range[1] ))
    
    bin_width= 230
    # here you can choose your rounding method, I've chosen math.ceil
    nbins = math.ceil((filted["salary_min"].max() - filted["salary_min"].min()) / bin_width)
     

    h_fig = px.histogram(filted, x = 'salary_min', nbins=nbins,
                         labels={"salary_min": "Salary in profile"},
                         color_discrete_sequence=['#432092 '],
                         title="Salary distribution")
    h_fig.update_traces(marker_line_width=2,marker_line_color="white")
    h_fig.layout.yaxis.title.text = 'Candidates hired'

    st.plotly_chart(h_fig)
