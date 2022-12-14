import streamlit as st
import pandas as pd
import plotly.express as px


COLOR_STATUS = {"Home":"#00cccc", "Away":"#cc00cc"}
COLOR_SEQ = ["#00cccc","#cc00cc"]
COLOR_CUSTOM = ["#00cccc"]

nfl_stats = pd.read_parquet("nfl_scores.parquet")
nfl_stats = nfl_stats.dropna()
nfl_stats["season_txt"] = nfl_stats["schedule_season"].astype("int")
nfl_stats["season_txt"] = nfl_stats["season_txt"].astype("str")

st.header("Filters")

#slider = 2000
#team = "TEN"

col1, col2 = st.columns(2)
with col1:
    team = st.selectbox("Team", nfl_stats.sort_values(["team_id"])["team_id"].unique())
    nfl_display = nfl_stats.loc[(nfl_stats["team_id"] == team)]
    min_year = int(nfl_display["schedule_season"].min())
with col2:
    slider = st.slider("Season", min_value=min_year, max_value=2020, value= [2011, 2022], step=1)

nfl_display = nfl_display.loc[nfl_display["schedule_season"].between(slider[0], slider[1], inclusive = "both")]
team_names_list = nfl_display["team"].unique().tolist()
team_names = ", ".join(team_names_list)
st.markdown(team_names)


st.header("Wins")
total_wins = nfl_display.groupby("status")["victory"].count()

away_wins = str(total_wins[0])
home_wins = str(total_wins[1])

col1, col2 = st.columns(2)
col1.metric("Home", home_wins)
col2.metric("Away", away_wins)


# Plot section
st.header("Plots")

## Cumulative wins plot
nfl_cumulative = nfl_display.groupby("schedule_week", as_index= False)["cumulative"].mean()


fig_wins = px.line(nfl_cumulative, x="schedule_week", y="cumulative",
                   color_discrete_sequence=COLOR_SEQ,
                   labels={
                       "schedule_week":"Week",
                       "cumulative":"Cumulative wins"
                   })
fig_wins.update_layout(plot_bgcolor="rgba(0,0,0,0)")
fig_wins.update_xaxes(showgrid=False)
fig_wins.update_yaxes(showgrid=False)


fig_cums = px.scatter(nfl_display, x="schedule_week", y="cumulative")

## Average score per season plot
fig_score = px.box(nfl_display, x="schedule_season", y="score", 
                   color_discrete_sequence=COLOR_CUSTOM,
                   labels={
                       "schedule_season":"Season", "score":"Score"
                   })
fig_score.update_layout(plot_bgcolor="rgba(0,0,0,0)")
fig_score.update_xaxes(showgrid=False)
fig_score.update_yaxes(showgrid=False)

## Win rate plot
prop_wins = nfl_display.groupby("schedule_season", as_index=False)["victory"].value_counts(normalize=True)
prop_wins = prop_wins.loc[prop_wins["victory"],  ["schedule_season", "proportion"]]
fig_prop = px.line(prop_wins, x="schedule_season", y="proportion", 
                   color_discrete_sequence=COLOR_CUSTOM, markers=True,
                   labels={
                       "proportion":"Win rate", 
                       "schedule_season":"Season"
                       })
fig_prop.update_layout(plot_bgcolor="rgba(0,0,0,0)")
fig_prop.update_xaxes(showgrid=False)
fig_prop.update_yaxes(showgrid=False)


## Win rate Home-Away plot
prop_wins_status = nfl_display.groupby(["schedule_season", "status"], as_index=False)
prop_wins_status = prop_wins_status["victory"].value_counts(normalize=True)
prop_wins_status = prop_wins_status.loc[prop_wins_status["victory"], ["schedule_season", "status", "proportion"]]
fig_status = px.line(prop_wins_status, x="schedule_season", y="proportion", color = "status", 
                     color_discrete_map=COLOR_STATUS, markers=True,
                     labels={
                         "schedule_season":"Season",
                         "proportion":"Win rate",
                         "status":"Home-Away"
                     })
fig_status.update_layout(plot_bgcolor="rgba(0,0,0,0)")
fig_status.update_xaxes(showgrid=False)
fig_status.update_yaxes(showgrid=False)

## Display plots
st.plotly_chart(fig_wins, use_container_width=True)
st.plotly_chart(fig_score, use_container_width=True)
st.plotly_chart(fig_prop, use_container_width=True)
st.plotly_chart(fig_status, use_container_width=True)


st.header("Stats")

st.dataframe(nfl_display)
