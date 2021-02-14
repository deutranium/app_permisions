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
        orgArr[org]['dangerous'] = 0
        orgArr[org]['signature'] = 0
    for j in data[org]:
        # item has a severity level defined
        if (j in perm_levels):
            level = perm_levels[j]

            orgArr[org][level] += 1

print(orgArr)

x = {}

for i in orgArr:
    x[i] = [orgArr[i][j] for j in orgArr[i]]

x = pd.DataFrame(x).T
x.columns = ["normal", "dangerous", "signature"]
st.write(x)

st.bar_chart(x)

orgs = []

for i in orgArr:
    orgs.append(i)

orgs = tuple(orgs)

org = st.selectbox(
    'Organization: ',
    orgs
)

# createPie(org)
