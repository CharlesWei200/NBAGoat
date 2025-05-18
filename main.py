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
		default_index = 3,
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
    col2.image(file_path+"Jordan_lebron.png")
    col1.markdown("I will be also comparing the effeciency of the two players by using the shooting percentage as high points could be achieved by taking more shoots which does not benifits the team for winning which means that it can not show that the player is better.")
        
    
    
    
    
    
    
    
    
if selected=='Data Cleaning':
    st.title("Data Cleaning")
    st.header("Why do we need to clean the data set before analysing?")
    st.write("### This is important because the data sets columns has problems such as data not in the same format which means it can not be analysed")
    st.divider()
    st.header("Players Position")
    st.write("### The Data set that I am using the position column has a problem that it has to many discrete positions such as Point Gard-Small Forward/Power Forward. This stops me from categorizing players and analysing more information so I had to find a way to make the positions less")
    col1,col2 = st.columns([5,5])
    col1.write("## Before Cleaning")
    col1.dataframe(players_df[["player","season","pos"]])
    col2.write("## After Cleaning")
    col2.dataframe(shooting[["player","season","clean_pos"]])
    st.markdown("### ***Click Below To View Code***")
    with st.expander("",icon=":material/code:"):
        st.code('''pos_dict = {"SG":"G",
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
                
        shooting["clean_pos"] = shooting["pos"].replace(pos_dict)
        award["clean_pos"] = players_df["pos"].replace(pos_dict)
                
                
                ''',language="python",line_numbers=True)
    st.write("### I decided to split to positions into 5 main categories Gaurd as G including point gaurd and shooting gaurd, Forward as F including small forward and power forward, Center as c and two additional positions gaurd forward which include both point gaurd and shooting gaurd and the two forwards, and Forward center which includes the two fowards and center init. I have stored this cleaned version of position in a new column as I might need the specific position in the future So its better not to overide it.")
    st.divider()
    st.header("Era")
    st.write("### For Further analysis I will have to split seasons into era's so that I can create the standard dieviation score column. I don't think it is a fair way to split seasons into eras by each 10 years as it does not have any impact on the game for example a game in 1989 would not be much different from one in 1990 so I decided to determine the eras based on the important rule changes such as removing hand check making offense easier so people in the future season scores more in average")
    st.markdown("### ***Click Below To View Code***")
    
    with st.expander("",icon=":material/code:"):
        st.code('''bins = [1947,1954,1980,1991,2005,2025]
players_df["era"] = pd.cut(players_df["season"],bins=bins,right=False,labels=["Early NBA","Early Modern Era","80's","90's","Modern NBA"])
                
                
                ''',language="python",line_numbers=True)
    st.write("### I Have chosen 1947, 1954, 1980, 1991, 2005, 2025 as the boundry for era's as in these years there has been important rule changes made to the NBA league such as banning hand check, adding three point line, adding paint area")
    st.divider()
    st.header("Standard Score")
    st.write("### Standard Score is a score that I have created to compare two different player that has not played in the same era. This score is usefull as players who has played in two different era has played in a different sets of rules, and played with different players that has different play style so simply comparing the basic stats of them is unfair. I have created the score by finding the mean of all player in the era that he has played in and how many standard dieviation he is above or below the mean. In this way I can see how outstanding is the player comparing to other players in the same era I believe that this is the best measurement of players ability")
    
    st.markdown("### ***Click Below To View Code***")
     
    with st.expander("",icon=":material/code:"):
         st.code('''def AvgRating(era,stats):
players_df.loc[players_df["era"]==era,stats].mean()

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

                 
                 
                 ''',language="python",line_numbers=True)       
    
    
    
    
    
    
    
    
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
    col1.markdown("### I will be comparing the two players By both offensive stat and defensive stats In this section I will compare the most basic stats of the two player such as point scored per game and assist per game.")
    col1.divider()
    col1.header("Comparing Offensive stats of player")
    col1.write("### As the box plot has shown on the right Michael Jordan is able to score more on aveerage and has a higher maximum points scored than Lebron, however lebron James has a smaller interquartile range so LeBron James can score more constantly")
    col1.write("### However, Lebron James has a higher average assist per game This means that LeBron James is able to make more plays score more points working with his teammates.")
    fig1 = px.box(players_df[players_df["player"].isin(["Michael Jordan","LeBron James"])],x="player",y="pts",color="player",color_discrete_sequence=color_pallet,title="Player Compared by points")
    col2.plotly_chart(fig1)
    fig1 = px.box(players_df[players_df["player"].isin(["Michael Jordan","LeBron James"])],x="player",y="ast",color="player",color_discrete_sequence=color_pallet,title="Player Compared by assist")
    col2.plotly_chart(fig1)
    
    col3,col4 = st.columns([3,5])
    col3.header("Compare the simple Defensive stats of LeBron and Jordan")
    col3.write("### Michael Jordan can get more steals on average this means that he is a better outlite defender and he can help is team to score more points from stealing.")
    col3.write("### Lebron James is better on blocking players this helps his team from reducing the enemy team from scoring. This is understandable as the position that LeBron and Jordan is playing on is different as Jordan is a Shooting Gaurd so he is better at gaurding outlit so he is able to steal more balls. And LeBron is a power forward so he works more in the paint and he's body is better at defending inside so easier to get more blocks.")
    fig1 = px.box(players_df[players_df["player"].isin(["Michael Jordan","LeBron James"])],x="player",y="stl",color="player",color_discrete_sequence=color_pallet,title="Player Compared by steals")
    col4.plotly_chart(fig1)
    fig1 = px.box(players_df[players_df["player"].isin(["Michael Jordan","LeBron James"])],x="player",y="blk",color="player",color_discrete_sequence=color_pallet,title="Player Compared by blocks")
    col4.plotly_chart(fig1)
    
    col5,col6 = st.columns([3,5])
    col5.title("Standard Deiviation Score")
    col5.write("### I decided to use standard score to compare the two  players Standard score is a score based on how the players stats compare to the average stats  of other players who played in their era. This score  is fair because it shows how they have dominated in their time and how much better they are playing in the same sets of rules")
#    col5.caption("Standard score is a score given in numbers of dieviation  the player is apart from the average player that played in their era")
    std_mean2 = get_mean_div(["Michael Jordan","LeBron James"],stat="stl",df_type="era")
    fig7 = px.histogram(std,x="player",y="standard",histfunc="avg",color_discrete_sequence=color_pallet,title="Players standard deiviation",color="player")

    col6.plotly_chart(fig7)
#    st.badge("StandardScore")  https://docs.streamlit.io/develop/api-reference/text/st.badge
    
    
    
    
if selected=='Conclusion':
    st.title("Conclusion")
    st.write("### In conclusion Michael Jordan and LeBron James are both outstanding or considerably the best player in their era that they have been playing in. They have both dominated in their era. However, it is hard to say which player is better as they has different style of game and they play in different position Michael Jordan is better at dominating the game by him self scoring stealing the ball. But LeBron James is a more team player he can help his teammates to score better to win the game and blocking shoots. By comparing all the stats of both player I would say that Michael Jordan is a better player as Jordan is a way better scorer than LeBron is at assisting and I believe that to determine who is a better player, the player should have the ablity to score and win by them selves so in that case Jordan is a better  player")
    
    
    
    
    
    
    
    
    
    
    
    
    
if selected=='Bibliography':
    st.title("Bibliography")
    st.markdown("[1] The 10 Rules That Changed the NBA Forever,By: Team Dunkest,https://www.dunkest.com/en/nba/news/196560/10-rules-changed-nba, 2025-3-20")
    st.markdown("[2] NBA Stats (1947-present),By: Sumitro Datta,https://www.kaggle.com/datasets/sumitrodatta/nba-aba-baa-stats/data, 2024-11-15")
    st.markdown("[3] New York Knickerbockers vs Fort Wayne Pistons Jan. 7, 1950,By: Sports Revisited,https://www.youtube.com/watch?v=_D6eLXIVDRg, 2025-4-2")
    st.markdown("[4] [FULL] LeBron James The Decision (7/8/2010) | ESPN Archives,By: ESPN,https://www.youtube.com/watch?v=Afpgnb_9bA4, 2025-4-2")
    st.markdown("[5] Image ,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6DUtuEZry0hZ3KHznGUxGqyeytR2jJuP2MQ&s, 2025-4-2")
    st.markdown("[6] Image ,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6DUtuEZry0hZ3KHznGUxGqyeytR2jJuP2MQ&s, 2025-4-2")
    st.markdown("[7] Image ,https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTTD-XoahiYRE3svZD-WYx9S92coR8QGPVl2Q&s, 2025-4-2")
    st.markdown("[8] Image ,https://e0.365dm.com/20/10/2048x1152/skysports-lebron-james-anthony-davis_5138168.jpg?20201014102448, 2025-4-2")
    st.markdown("[9]Image ,https://m.media-amazon.com/images/I/51oaUD8NcLL._AC_UF894,1000_QL80_.jpg, 2025-4-2")
    st.markdown("[10] Image ,https://cdn.nba.com/manage/2021/07/GettyImages-2928222.jpg, 2025-4-2")
    st.markdown("[11] Image ,https://cdn.nba.com/manage/2021/07/GettyImages-2928222.jpg, 2025-4-2")
    st.markdown("[12] Image ,https://www.rollingstone.com/wp-content/uploads/2020/05/the-last-dance-eps-5-6.jpg?w=1581&h=1054&crop=1, 2025-4-2")
    st.markdown("[13] Image ,https://dims.apnews.com/dims4/default/323aff6/2147483647/strip/true/crop/2000x2559+0+0/resize/468x599!/quality/90/?url=https%3A%2F%2Fstorage.googleapis.com%2Fafs-prod%2Fmedia%2Ffd45e78526234a1b8d103856ed41d427%2F2000.jpeg, 2025-4-2")
    st.markdown("[14] Image ,https://pbs.twimg.com/media/FVnuGVsWIAAWXgO.jpg:large, 2025-4-2")
    st.markdown("[15] Image ,https://a.espncdn.com/photo/2019/0414/r528886_1296x729_16-9.jpg, 2025-4-2")
    st.markdown("[16] Image ,https://cdn.nba.com/teams/legacy/i.cdn.turner.com/nba/nba/.element/media/2.0/teamsites/bucks/90s-players-ewing.jpg, 2025-4-2")
    st.markdown("[17] Image ,https://cdn.nba.com/manage/2021/07/GettyImages-1737696-1568x882.jpg, 2025-4-2")
    st.markdown("[18] Image ,https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Wilt_Chamberlain_100_Point_Game_1962_%28original%29.jpg/250px-Wilt_Chamberlain_100_Point_Game_1962_%28original%29.jpg, 2025-4-2")
    st.markdown("[19] Image ,https://www.nba.com/, 2025-4-2")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
