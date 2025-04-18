import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import streamlit as st
from streamlit_timeline import timeline
from streamlit_option_menu import option_menu
import json

file_path = ""


st.set_page_config(layout="wide")

color_pallet = ["#b3b3ff","#1affff","#ccffcc","#ff9999","#4dff4d","#669999","#0099cc","#009900","#ff6600","#ffcc00",
                "#cc33ff","#ffcccc","#ffffcc","#ccff66","#cc6699","#ff33cc","#cc0066","#ff9900","#ff99ff","#99ff66",
                "#ffcc99","#ff6600","#3399ff","#00ccff","#3366ff","#0099cc","#333399","#00ff99","#990099","#ff9999"]

pos_dict = {"SG":"G",
            "PG":"G",
            "SF":"F",
            "PF":"F",
            "SG-PG":"G",
            "PG-SG":"G",
            "SF-PF":"F",
            "PF-SF":"F",
            "C-F":"F-C",
            "F-G":"G-F",
            "C-SF":"F-C",
            "PG-SF":"G-F",
            "SG-PF":"G-F",
            "SF-C":"F-C",
            "SG-PG-SF":"G-F",
            "SG-SF":"G-F",
            "PF-C":"C",
            "C-PF":"F-C",
            "SF-PG":"G-F",
            "SF-SG":"G-F"
            }


#dictionaries for better column display name
num_var = {"g":"Games Played",
           "fg":"Field Goal",
           "fga":"Field Goal Attempt",
           "fg_percent":"Field Goal %",
           "orb":"Offensive Rebound",
           "drb":"Defensive Rebound",
           "trb":"Total Rebound",
           "ast":"Assist",
           "stl":"Steal",
           "blk":"Block",
           "pts":"Points"}

cat_var = {"player":"Name",
           "clean_pos":"Position",
           "lg":"League",
           "tm":"Team"
           }

all_var = num_var.copy()
all_var.update(cat_var)



shooting = pd.read_csv(file_path+"Shooting.csv")
award = pd.read_csv(file_path+"Award.csv")
players_df=pd.read_csv(file_path+"Players.csv")

award_winners = award[award["winner"]==True].copy

mvp = award[award["award"]=="nba mvp"].copy()
mvp_winner = mvp[mvp["winner"]==True].copy()

melt = pd.melt(frame=award.copy(),
               id_vars="player",
                  value_vars=["pts_won","pts_max"],
                  var_name="won_max",
                  value_name="pts")

clutch = award[award["award"]=="clutch_poy"].copy()

steph = shooting[shooting["player"]=="Stephen Curry"].sort_values("season").copy()

dpoy = award[award["award"]=="dpoy"].copy()

award_player = pd.merge(left=players_df,right=award,on="player",how="outer")

shooting["clean_pos"] = shooting["pos"].replace(pos_dict)
award["clean_pos"] = players_df["pos"].replace(pos_dict)

grouped = award.groupby("clean_pos")["pts_max"]
award_won = award.groupby("clean_pos")["winner"]

win_count = award_won.count()

#Creating winner column
#era column
bins = [1947,1954,1980,1991,2005,2025]
players_df["era"] = pd.cut(players_df["season"],bins=bins,right=False,labels=["Early NBA","Early Modern Era","80's","90's","Modern NBA"])

key_stats = ["pts","ast","stl","blk"]
players_era = players_df[["player","era"]+key_stats].groupby(["player","era"],observed=False).sum().reset_index()
players_era["sum_stats"] = players_era[key_stats].sum(axis=1)
players_era = players_era[players_era["sum_stats"] > 0].copy()



#function for getting mean and stadard dieviation for each player
def get_mean_div(players,stat,df_type):
    #Getting how the mean and stadard dieviation should be calculated by each era or season the player has played in
    if df_type == "era":
        df = players_era
    elif df_type == "season":
        df = players_df
    else:
        print("df_type not must be era or season")
        return None
    #creating a temporary data frame of a copy of player to manipulate the data 
    temp_df = df[df["player"].isin(players)].reset_index(drop=True).copy()
    #getting the average for all the other player that has been playing in the group(era,season)
    group_means = dict(df.groupby(df_type,observed=False)[stat].agg("mean"))
    #getting the stadard dieviation all the other people in the group
    group_std = dict(df.groupby(df_type,observed=False)[stat].agg("std"))
    
    #finding the players different by subtracting group mean and std by players mean and std
    def subtract_mean(row):
        #getting the group values
        group = row[df_type]
        #calculating the mean differnt
        mean_dev = row[stat] - group_means[group]
        #calculating the std difference
        standard_score = mean_dev/group_std[group]
        return mean_dev,standard_score
    
    #apply the function to aggragate and find value
    test = pd.DataFrame(list(temp_df.apply(subtract_mean,axis=1)),columns=[stat+"_diff","standard"])
    
    return pd.concat([temp_df,test],axis=1)
    
    
std = get_mean_div(["Michael Jordan","LeBron James"],stat="pts",df_type="era")



def AvgRating(era,stats):
    players_df.loc[players_df["era"]==era,stats].mean()
    
    


with st.sidebar: 
	selected = option_menu(
		menu_title = 'Navigation Bar',
		options = ['Abstract', 'Timeline','Background Information', 'Data Cleaning','Exploratory Analysis', 'Main Analysis', 'Conclusion', 'Bibliography'],
		menu_icon = 'dribbble',
		icons = ['file-person', 'calendar3','backpack3', 'trash', 'map', 'bar-chart-line', 'award', 'browser-chrome'],
		default_index = 5,
		)








if selected=='Abstract':
    st.title("Abstract")
    st.markdown("This is my NBA case study")
    
    
    
    
    
    
    

if selected=='Timeline':
    st.title("Timeline")
    
    with open("timeline.json","r") as f:
        data = json.load(f)

    timeline(data)







if selected=='Background Information':
    st.title("Background Information")
    col1,col2 = st.columns([5,4])
    col1.markdown("## Why do I want to compare `LeBron James` with `Michael Jordan`")
    col1.markdown("""Michael Jordan Have been seen as the Greatest Basketball Player of all time since the 90's from both achievements and how he has affected the sport basketball, However there has been conversation about whether LeBron James is better than Jordan now. since LeBron James has won multiple champions and
                  broke the total score record more and more people are starting to believe that LeBron is a better player""")
    col1.markdown("## How would I compare the two player?")
    col1.markdown("""I have found data sets on kaggle about all the data's in the previous NBA season which include point scored assist and many others I have chosen three main data set to use one standard information and one about a award, However it is unfair to compare player from different era's
                  based on simple statistics such as points scored because they have played in different sets of rules and the skills sets, for example banning handcheck for defending makes scoring much more easier and smaller players are able to play players has been scoring way more than before. Therefore I have decided to calculate a standard value to compare them. By using the mean and standard deiviation of all the other players that have
                  played in their era.By calculating how many standard dieviation away from other player that has played in there era I can see how stand out LeBron or Jordan is from their era I believe that by this is a fair way to compare the two players. Additionally Jordan and LeBron have played different amounts of games so using the average stats per game is a better way to compare them.""")
    col2.image("Jordan_Lebron.png")
    col1.markdown("I will be also comparing the effeciency of the two players by using the shooting percentage as high points could be achieved by taking more shoots which does not benifits the team for winning which means that it can not show that the player is better.")
        
    
    
    
    
    
    
    
    
if selected=='Data Cleaning':
    st.title("Data Cleaning")
    
    
    
    
    
    
    
    
    
if selected=='Exploratory Analysis':
    st.title("Exploratory Analysis")
    st.header("Exploring Data By Player")
    st.markdown("These graph allows you compares players based on selected statistics")
    
    st.subheader("Histograms")
    col1,col2 = st.columns([3,5])
    col1.markdown("Select up to 10 Players for the x A statistic numerical column for y")
    
    with st.form("Exploring Histograms by Players"):
        Player_Select = col1.multiselect("Select up to 10 Players",shooting["player"].unique(),default=["Michael Jordan","LeBron James"],max_selections=10,key=1)
        y_col1 = col1.selectbox("Select A Numerical statistcal catagory",["fg_percent","avg_dist_fga"],key=2)
        col1_agg = col1.radio("Select one:",["Career Totals","Average Per Game"],key=3)
        col1_histfunc = "sum" if col1_agg == "Career Totals" else "avg" 
        
        
        submitted=st.form_submit_button("Submit to produce the histogram")
        if submitted:
            fig1 = px.histogram(shooting[shooting["player"].isin(Player_Select)],x="player",y=y_col1,color="player",color_discrete_sequence=color_pallet,histfunc=col1_histfunc,title=f"Player Comparison by {y_col1}")
            fig1.update_yaxes(title_text=col1_agg)
            col2.plotly_chart(fig1)
            
            
    #Second Graph
    st.header("Exploring data by Stats")
    st.markdown("This Graph Compares Player using The stats")
    
    col3,col4 = st.columns([3,5])
    col3.markdown("Select up to 5 players")
    with st.form("Exploring points statistics through histograms"):
        Player_Select2 = col3.multiselect("Select up to 5 players",players_df["player"].unique(),default=["Michael Jordan","LeBron James"],max_selections=5,key=4)
        y_col2 = col3.selectbox("Select a Numeric statistic to compare",list(num_var.values()),key=5)
        col2_agg = col3.radio("Select One",["Career Totals","Average Per Game"],key=6)
        col2_histfunc = "sum" if col2_agg == "Career Totals" else "avg"
        
        submitted = st.form_submit_button("Submit to produce the histogram")
        
        y_col2_df = [key for key,value in num_var.items() if value==y_col2][0]
        
        
        if submitted:
            fig2 =  px.histogram(players_df[players_df["player"].isin(Player_Select2)],x="player",y=y_col2_df,color="player",color_discrete_sequence=color_pallet,histfunc=col2_histfunc,title=f"Player Compared by {y_col2}",labels=all_var)
            fig2.update_yaxes(title_text=col2_agg)
            fig2.update_yaxes(title_text=f"<b>{col2_agg} For {y_col2}</b>")
            col4.plotly_chart(fig2)
            
        
        
    #third Graph
    st.header("Comparing Player with")
    st.markdown("This Graph Compares Player using The Awards that they have won")
    
    col5,col6 = st.columns([3,5])
    col5.markdown("Select up to 5 players")
    with st.form("Exploring points statistics through box plot"):
        Player_Select3 = col5.multiselect("Select up to 5 players",players_df["player"].unique(),default=["Michael Jordan","LeBron James"],max_selections=5,key=7)
        y_col3 = col5.selectbox("Select a Numeric statistic to compare",["pts","ast","blk","stl"],key=9)
        
        submitted = st.form_submit_button("Submit to produce the histogram")
        
        if submitted:
            fig2 =  px.box(players_df[players_df["player"].isin(Player_Select3)],x="player",y=y_col3,color="player",color_discrete_sequence=color_pallet,title=f"Player Compared by {y_col2}")
            col6.plotly_chart(fig2)
    
    
    #Fourth Graph
    st.header("Exploring data by Award")
    st.markdown("This Graph Compares Player using The Awards that they have won")
    
    col7,col8 = st.columns([3,5])
    col7.markdown("Select up to 5 players")
    with st.form("Exploring points statistics through ability"):
        Player_Select4 = col7.multiselect("Select up to 5 players",players_df["player"].unique(),default=["Michael Jordan","LeBron James"],max_selections=5,key=11)
        y_col4 = col7.selectbox("Select a Numeric statistic to compare",["score_diff","asist_diff","block_diff","steal_diff"],key=12)
        
        submitted = st.form_submit_button("Submit to produce the histogram")
        
        if submitted:
            fig4 =  px.histogram(players_era[players_era["player"].isin(Player_Select4)],x="player",y=y_col4,color="era",color_discrete_sequence=color_pallet,title=f"Player Compared by {y_col4}")
            col8.plotly_chart(fig4)
            
            
            
            
    #Fifth Graph
    st.header("Exploring data by Sunburst")
    st.markdown("This Graph gives explores data through sunburst")
    
    col9,col10 = st.columns([3,5])
    col9.markdown("Select up to 5 players")
    with st.form("Exploring points statistics through sunburst graph"):
        Path_Select5 = col9.multiselect("Select the path",["season","era","lg","tm"],max_selections=5,key=13)
        y_col5 = col9.selectbox("Select a Numeric statistic to compare",["pts","ast","blk","stl"],key=14)
        
        submitted = st.form_submit_button("Submit to produce the histogram")
        
        if submitted:
            fig5 =  px.sunburst(players_df,path=Path_Select5,values=y_col5,color_discrete_sequence=color_pallet,title=f"Player Compared by {y_col5}")
            col10.plotly_chart(fig5)
    
    
    #six Graph
    st.header("Determine players style through sunburst")
    
    col11,col12 = st.columns([3,5])
    with st.form("Exploring Players Style through sunburst graph"):
        Path_Select6 = col11.multiselect("Select up to 5 players",["player","season","era","lg","tm"],max_selections=5,default=["player"],key=15)
        y_col6 = col11.selectbox("Select a Numeric statistic to compare",["pts","ast","blk","stl"],key=16)
        Player_Select6 = col11.multiselect("Select up to 5 players",players_df["player"].unique(),default=["Michael Jordan","LeBron James"],max_selections=5,key=17)
        submitted = st.form_submit_button("Submit to produce the Sunburst")
        
        if submitted:
            fig6 =  px.sunburst(players_df[players_df["player"].isin(Player_Select6)],path=Path_Select6,values=y_col6,color_discrete_sequence=color_pallet,title=f"Player Compared by {y_col6}")
            col12.plotly_chart(fig6)
    
    #Seventh Graph
    st.header("Exploring players through std and mean")
    
    col11,col12 = st.columns([3,5])
    with st.form("Exploring Players style through standard deiviation"):
        player_select7 = col11.multiselect("Select up to 8 players",players_df["player"].unique(),default=["Michael Jordan","LeBron James"],max_selections=8,key=18)
        y_col7 = col11.selectbox("Select a Numeric statistic to compare",["pts","ast","stl","blk","rbd"],key=19)
        comp_type = col11.selectbox("Compare by season or by era",["era","season"],key=20)
        submitted = st.form_submit_button("Submit to produce a bar chart")
        
        if submitted:
            std_mean = get_mean_div(player_select7,stat=y_col7,df_type=comp_type)
            fig7 = px.histogram(std_mean,x="player",y="standard",histfunc="avg",hover_data="standard",color_discrete_sequence=color_pallet,title="Players standard deiviation",color="player")
            col12.plotly_chart(fig7)
            
        
    
    
    
    
    
    
if selected=='Main Analysis':
    st.title("Main Analysis")
    col1,col2 = st.columns([3,5])
    col1.header("First we can compare the simple stats of LeBron and Jordan")
    col1.markdown("I will be comparing the two players By both offensive stat and defensive stat")
    fig1 = px.box(players_df[players_df["player"].isin(["Michael Jordan","LeBron James"])],x="player",y="pts",color="player",color_discrete_sequence=color_pallet,title="Player Compared by points")
    col2.plotly_chart(fig1)
    fig1 = px.box(players_df[players_df["player"].isin(["Michael Jordan","LeBron James"])],x="player",y="ast",color="player",color_discrete_sequence=color_pallet,title="Player Compared by assist")
    col2.plotly_chart(fig1)
    
    col3,col4 = st.columns([3,5])
    col3.header("First we can compare the simple stats of LeBron and Jordan")
    fig1 = px.box(players_df[players_df["player"].isin(["Michael Jordan","LeBron James"])],x="player",y="stl",color="player",color_discrete_sequence=color_pallet,title="Player Compared by assist")
    col4.plotly_chart(fig1)
    fig1 = px.box(players_df[players_df["player"].isin(["Michael Jordan","LeBron James"])],x="player",y="blk",color="player",color_discrete_sequence=color_pallet,title="Player Compared by assist")
    col4.plotly_chart(fig1)
    
    col5,col6 = st.columns([3,5])
    std_mean2 = get_mean_div(["Michael Jordan","LeBron James"],stat="stl",df_type="era")
    fig7 = px.histogram(std,x="player",y="standard",histfunc="avg",color_discrete_sequence=color_pallet,title="Players standard deiviation",color="player")
    col6.plotly_chart(fig7)
    
    
    
    
    
if selected=='Conclusion':
    st.title("Conclusion")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
if selected=='Bibliography':
    st.title("Bibliography")
    st.markdown("The 10 Rules That Changed the NBA Forever,By: Team Dunkest,https://www.dunkest.com/en/nba/news/196560/10-rules-changed-nba, 2025-3-20")
    st.markdown("NBA Stats (1947-present),By: Sumitro Datta,https://www.kaggle.com/datasets/sumitrodatta/nba-aba-baa-stats/data, 2024-11-15")
    st.markdown("New York Knickerbockers vs Fort Wayne Pistons Jan. 7, 1950,By: Sports Revisited,https://www.youtube.com/watch?v=_D6eLXIVDRg, 2025-4-2")
    st.markdown("[FULL] LeBron James The Decision (7/8/2010) | ESPN Archives,By: ESPN,https://www.youtube.com/watch?v=Afpgnb_9bA4, 2025-4-2")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
