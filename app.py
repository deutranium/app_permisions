import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

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
        orgArr[org]['normal'] = 0
        orgArr[org]['signature'] = 0
        orgArr[org]['dangerous'] = 0
    for j in data[org]:
        # item has a severity level defined
        if (j in perm_levels):
            level = perm_levels[j]

            orgArr[org][level] += 1

x = {} # dataframe to be plotted

for i in orgArr:
    x[i] = [orgArr[i][j] for j in orgArr[i]]

x = pd.DataFrame(x).T
x.columns = ["normal", "signature", "dangerous"]



st.title("Smartphone Apps and access to restricted data")

st.write("Our smartphones have the ability to monitor a lot of our activity and are \
         privy to most of our sensitive data. Apps have the ability to access this \
         with the help of permissions. Android requires apps to declare the various \
         agencies that they require, but as these can be numerous and tedious to review \
         for a user, they are grouped into three major categories - Normal, Dangerous and Signature.")

st.bar_chart(x)

st.header("Visualisation")
st.write("We have taken a dataset of the permissions declared by the top 25 apps \
         and showcased what portion of them come under Dangerous or Normal. Bear \
         in mind that the number of permissions that these apps require varies.") #and \
         #can be observed by hovering over the chart.")

#createPie(org)

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
