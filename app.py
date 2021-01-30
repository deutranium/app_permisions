import streamlit as st
import plotly.express as px
import numpy as np

import requests
from lxml import etree

import json

from streamlit_echarts import st_echarts

# getting perm levels
url = "https://developer.android.com/reference/android/Manifest.permission#constants_1"

req = requests.get(url)
lxml = etree.HTML(req.text)


def protection(line):
    if line.startswith("Protection level: "):
        return True
    else:
        return False


def constant(line):
    if line.startswith("Constant Value:"):
        return True
    else:
        return False


data = lxml.xpath("//*[@id=\"jd-content\"]/div/p/text()")

perm_levels = {}


for lp, lc in zip(filter(protection, data), filter(constant, data)):
    permission = lc.split("\"")[-2].split(".")[-1]
    level = lp.strip("\n ").split("Protection level: ")[1].split("|")[0]

    perm_levels[permission] = level

# print(perm_levels)


# Getting data and analyzing it

path = "Top25Global.json"

with open(path) as fp:
    data = json.load(fp)


orgArr = {}

for i in data:
    org = i
    org_levels = {}

    orgArr[i] = {}

    # per item per org
    for j in data[org]:

        # item has a severity level defined
        if (j in perm_levels):
            level = perm_levels[j]

            # if level already there for this org
            if (level in orgArr[org]):
                orgArr[org][level] += 1
            else:
                orgArr[org][level] = 1

pieArr = {}

for i in orgArr:
    pieArr[i] = []

    for j in orgArr[i]:
        pieArr[i].append({"value": orgArr[i][j], "name": j})


def createPie(org):
    pie_options = {
            "backgroundColor": "#2c343c",
            "title": {
                "text": "Distribution in levels of permissions",
                "left": "center",
                "top": 20,
                "textStyle": {"color": "#ccc"},
            },
            "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b} : {c} ({d}%)"},
            "visualMap": {
                "show": True,
                "min": -5,
                "max": 10,
                # "inRange": {"colorLightness": [0, 1]},
            },
            "series": [
                {
                    "name": "Distribution in levels of permissions",
                    "type": "pie",
                    "radius": "55%",
                    "center": ["50%", "50%"],
                    "data": pieArr[org],
                    # "roseType": "radius",
                    "label": {"color": "rgba(255, 255, 255, 0.3)"},
                    "labelLine": {
                        "lineStyle": {"color": "rgba(255, 255, 255, 0.3)"},
                        "smooth": 0.2,
                        "length": 10,
                        "length2": 20,
                    },
                    "itemStyle": {
                        "color": "#c23531",
                        "shadowBlur": 200,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    },
                    "animationType": "scale",
                    "animationEasing": "elasticOut",
                }
            ],
        }
    st_echarts(options=pie_options, key=org)


orgs = []

for i in orgArr:
    orgs.append(i)

orgs = tuple(orgs)

st.title("Smartphone Apps and access to restricted data")

st.write("Our smartphones have the ability to monitor a lot of our activity and are \
         privy to most of our sensitive data. Apps have the ability to access this \
         with the help of permissions. Android requires apps to declare the various \
         agencies that they require, but as these can be numerous and tedious to review \
         for a user, they are grouped into three major categories - Normal, Dangerous and Signature.")

org = st.selectbox(
    'Organization: ',
    orgs
)

st.header("Visualisation")
st.write("We have taken a dataset of the permissions declared by the top 25 apps \
         and showcased what portion of them come under Dangerous or Normal. Bear \
         in mind that the number of permissions that these apps require varies and \
         can be observed by hovering over the chart.")

createPie(org)

st.header("Types of Permissions")
st.subheader("Normal Permissions")
st.write("If there is a very little or no risk of the user's privacy \
         then the permission comes under the Normal Permission category. \
         For example, if an app wants to get the date and time, then it \
         does not need to ask the user for authorisation. They still need \
         to declare it to the system and the OS will grant them the ability \
         when the app is installed.")

st.subheader("Signature Permissions")
st.write("This is a special set of permissions to enable safe data \
         access between apps owned by the same developer or company.")

st.subheader("Dangerous Permissions")
st.write("Dangerous permissions include those permissions that involve \
         user data in some or the other way. For example, to read contacts \
         from the phone or to access the file storage of the phone. These \
         permissions can compromise user privacy and hence, require explicit \
         acceptance from the user.")
