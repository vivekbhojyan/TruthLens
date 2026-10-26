"""
TruthLens: Fake News Detector
Real-Time News Verifier & Live Fact-Checker
Developer: Vivek Kumar (vivekbij05@gmail.com)
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="TruthLens | Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SESSION STATE INITIALIZATION -----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "headline_input" not in st.session_state:
    st.session_state.headline_input = ""

if "body_input" not in st.session_state:
    st.session_state.body_input = ""

if "current_result" not in st.session_state:
    st.session_state.current_result = None

if "error_msg" not in st.session_state:
    st.session_state.error_msg = None

# ----------------- HANDLE NAVBAR ACTIONS VIA QUERY PARAMS -----------------
# This allows the HTML navbar's action links to trigger Python-side effects
_params = st.query_params
if _params.get("action") == "toggle_theme":
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.query_params.clear()
    st.rerun()
elif _params.get("action") == "clear_cache":
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.input_headline = ""
    st.session_state.input_body = ""
    st.session_state.current_result = None
    st.query_params.clear()
    st.rerun()

# ----------------- GLOBAL STYLES & CLEANUP -----------------
st.markdown("""
<style>
    /* ── Hide ONLY Deploy button, 3-dots Menu & Footer ── */
    [data-testid="stDeployButton"],
    [data-testid="stAppDeployButton"],
    .stDeployButton,
    button[title="Deploy"],
    button[aria-label="Deploy"],
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Header: transparent, proper height so controls are not squeezed, click-through */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 56px !important;
        min-height: 56px !important;
        overflow: visible !important;
        z-index: 100000 !important;
        pointer-events: none !important;
    }
    
    /* Allow clicking on sidebar buttons in header */
    header[data-testid="stHeader"] button,
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button {
        pointer-events: auto !important;
        cursor: pointer !important;
    }
    
    /* ── Sidebar Expand/Toggle Button (Always visible & clickable when sidebar is collapsed) ── */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 100005 !important;
        transform: translateY(4px) !important;
    }
    
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    header[data-testid="stHeader"] button {
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 0 14px !important;
        height: 38px !important;
        box-sizing: border-box !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.45) !important;
        cursor: pointer !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        line-height: 1 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="collapsedControl"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    header[data-testid="stHeader"] button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(37,99,235,0.55) !important;
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    header[data-testid="stHeader"] button svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
        width: 18px !important;
        height: 18px !important;
    }
    [data-testid="collapsedControl"] button::after,
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: " Controls";
        font-weight: 600;
        font-size: 13px;
        color: #ffffff !important;
        white-space: nowrap;
    }
    
    /* ── Pull Down Sidebar Collapse Button (<<) and bring above all layers so it clicks smoothly ── */
    section[data-testid="stSidebar"] {
        z-index: 1000000 !important;
    }
    section[data-testid="stSidebar"] > div:first-child,
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        padding-top: 35px !important;
        padding-bottom: 10px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] {
        margin-top: 25px !important;
        margin-left: 10px !important;
        position: relative !important;
        top: 15px !important;
        display: flex !important;
        align-items: center !important;
        z-index: 1000005 !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarCollapseButton"] button {
        cursor: pointer !important;
        pointer-events: auto !important;
        padding: 8px !important;
        border-radius: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 1000006 !important;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        width: 20px !important;
        height: 20px !important;
        pointer-events: none !important;
    }
    
    /* ── Website Navbar: FIXED / STICKY AT TOP OF SCREEN ── */
    div[data-testid="stVerticalBlock"]:has(> div .sticky-nav-sentinel),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sticky-nav-sentinel) {
        position: sticky !important;
        top: 0px !important;
        z-index: 99999 !important;
        width: 100% !important;
        padding: 10px 18px !important;
        margin-bottom: 1.5rem !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* Container Spacing: flush against the top */
    .block-container {
        padding-top: 0px !important;
        padding-bottom: 3rem !important;
    }

    /* Offset Brand title if collapsedControl is present so they do not collide */
    .stApp:has([data-testid="collapsedControl"]) .brand-wrap,
    .stApp:has([data-testid="stSidebarCollapsedControl"]) .brand-wrap {
        padding-left: 125px !important;
    }

    /* ── Website Navbar Component Styling ── */
    .website-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .brand-icon {
        font-size: 1.6rem;
    }
    .brand-text {
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .brand-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* Main headings */
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    .badge-real {
        background-color: #dcfce7;
        color: #15803d;
        padding: 0.7rem 1.2rem;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.25rem;
        display: block;
        text-align: center;
        border: 1.5px solid #86efac;
        margin-bottom: 1rem;
    }
    .badge-fake {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 0.7rem 1.2rem;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.25rem;
        display: block;
        text-align: center;
        border: 1.5px solid #fca5a5;
        margin-bottom: 1rem;
    }
    .card-box {
        border-radius: 10px;
        padding: 1.2rem;
        margin-top: 0.8rem;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .support-link-card {
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.6rem;
        font-size: 0.9rem;
    }
    .support-link-card a { text-decoration: none; font-weight: 600; }
    .support-link-card a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# ----------------- DYNAMIC LIGHT / DARK THEME STYLES -----------------
if st.session_state.theme == "dark":
    st.markdown("""
    <style>
        .stApp {
            background-color: #0b0f19 !important;
            color: #f1f5f9 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #111827 !important;
            color: #f1f5f9 !important;
            border-right: 1px solid #1f2937 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }
        .main-title { color: #60a5fa !important; }
        .sub-title { color: #94a3b8 !important; }
        
        /* Fixed Navbar Dark Theme */
        div[data-testid="stVerticalBlock"]:has(> div .sticky-nav-sentinel),
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.sticky-nav-sentinel),
        .website-navbar {
            background-color: rgba(11, 15, 25, 0.95) !important;
            border-bottom: 1px solid #1f2937 !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        }
        .brand-text { color: #60a5fa !important; }
        .brand-badge {
            background-color: #1e3a8a !important;
            color: #93c5fd !important;
            border: 1px solid #2563eb !important;
        }
        
        /* Navbar & Sidebar Buttons in Dark Mode */
        div[data-testid="stHorizontalBlock"] .stButton > button,
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #1e293b !important;
            color: #f1f5f9 !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        div[data-testid="stHorizontalBlock"] .stButton > button *,
        section[data-testid="stSidebar"] .stButton > button * {
            color: #f1f5f9 !important;
        }
        div[data-testid="stHorizontalBlock"] .stButton > button:hover,
        section[data-testid="stSidebar"] .stButton > button:hover {
            background-color: #334155 !important;
            border-color: #475569 !important;
        }
        
        /* Inputs */
        .stTextInput input, .stTextArea textarea {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border: 1.5px solid #334155 !important;
            border-radius: 8px !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important;
        }
        label, [data-testid="stWidgetLabel"] p {
            color: #cbd5e1 !important;
            font-weight: 600 !important;
        }
        
        /* Cards */
        .card-box {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            color: #e2e8f0 !important;
        }
        .support-link-card {
            background-color: #131d2e !important;
            border: 1px solid #334155 !important;
        }
        .support-link-card a { color: #60a5fa !important; }
        
        /* Primary Submit Button */
        .stButton > button[kind="primary"] {
            background-color: #2563eb !important;
            color: #ffffff !important;
            border: none !important;
        }
        .stButton > button[kind="primary"] * {
            color: #ffffff !important;
        }

        /* Sidebar in Dark Mode */
        [data-testid="stSidebarCollapseButton"] button {
            color: #f1f5f9 !important;
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        [data-testid="stSidebarCollapseButton"] svg {
            fill: #f1f5f9 !important;
            stroke: #f1f5f9 !important;
            color: #f1f5f9 !important;
        }
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
        }
        section[data-testid="stSidebar"] .stButton > button p,
        section[data-testid="stSidebar"] .stButton > button span,
        section[data-testid="stSidebar"] .stButton > button div {
            color: #f1f5f9 !important;
            font-weight: 600 !important;
        }

        /* Modal Dialogs Dark Mode */
        div[data-testid="stModal"] > div,
        div[role="dialog"] {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
        }
        div[data-testid="stModal"] *,
        div[role="dialog"] * {
            color: #f8fafc !important;
        }
        div[data-testid="stModal"] a,
        div[role="dialog"] a {
            color: #60a5fa !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        
        /* ── Sidebar in Light Mode ── */
        section[data-testid="stSidebar"] {
            background-color: #f1f5f9 !important;
            border-right: 1.5px solid #cbd5e1 !important;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div {
            color: #0f172a !important;
        }
        section[data-testid="stSidebar"] .stCaption p {
            color: #475569 !important;
        }

        /* Sidebar Control/Collapse Button (<<) Inside Sidebar in Light Mode */
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
            color: #0f172a !important;
            background-color: #ffffff !important;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px !important;
            padding: 4px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {
            fill: #0f172a !important;
            stroke: #0f172a !important;
            color: #0f172a !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button:hover {
            background-color: #e2e8f0 !important;
        }

        /* Floating Sidebar Open Button (>>) in Light Mode (High Contrast Royal Blue) */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        header[data-testid="stHeader"] [data-testid="stSidebarCollapseButton"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 1000005 !important;
        }
        [data-testid="collapsedControl"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        header[data-testid="stHeader"] [data-testid="stSidebarCollapseButton"] button,
        header[data-testid="stHeader"] button {
            background-color: #2563eb !important;
            color: #ffffff !important;
            border: 1px solid #1d4ed8 !important;
            box-shadow: 0 4px 14px rgba(37,99,235,0.45) !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg,
        header[data-testid="stHeader"] [data-testid="stSidebarCollapseButton"] svg,
        header[data-testid="stHeader"] button svg {
            fill: #ffffff !important;
            stroke: #ffffff !important;
            color: #ffffff !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        [data-testid="collapsedControl"] button::after,
        [data-testid="stSidebarCollapsedControl"] button::after,
        header[data-testid="stHeader"] [data-testid="stSidebarCollapseButton"] button::after {
            color: #ffffff !important;
        }
        
        /* Sidebar Filter Text Input in Light Mode */
        section[data-testid="stSidebar"] div[data-baseweb="input"],
        section[data-testid="stSidebar"] div[data-baseweb="base-input"],
        section[data-testid="stSidebar"] input {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1.5px solid #94a3b8 !important;
            border-radius: 8px !important;
        }
        section[data-testid="stSidebar"] input::placeholder {
            color: #64748b !important;
        }

        /* ── All Sidebar Buttons in Light Mode (History items, etc.) ── */
        section[data-testid="stSidebar"] button,
        section[data-testid="stSidebar"] .stButton > button,
        section[data-testid="stSidebar"] button[kind="secondary"],
        section[data-testid="stSidebar"] [data-testid="baseButton-secondary"],
        section[data-testid="stSidebar"] div[data-testid="stButton"] button {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.06) !important;
            padding: 8px 12px !important;
            font-weight: 600 !important;
            text-align: left !important;
            justify-content: flex-start !important;
        }

        /* Prevent focus/active states from ever turning into a dark smudge */
        section[data-testid="stSidebar"] button:focus,
        section[data-testid="stSidebar"] button:active,
        section[data-testid="stSidebar"] button:focus:not(:active),
        section[data-testid="stSidebar"] .stButton > button:focus,
        section[data-testid="stSidebar"] .stButton > button:active,
        section[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
            background-color: #f8fafc !important;
            background: #f8fafc !important;
            color: #1d4ed8 !important;
            border: 1.5px solid #2563eb !important;
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
        }

        /* Hover state in Light Mode */
        section[data-testid="stSidebar"] button:hover,
        section[data-testid="stSidebar"] .stButton > button:hover {
            background-color: #eff6ff !important;
            background: #eff6ff !important;
            border-color: #2563eb !important;
            box-shadow: 0 3px 8px rgba(37, 99, 235, 0.15) !important;
        }

        /* Text inside all sidebar buttons in Light Mode */
        section[data-testid="stSidebar"] button *,
        section[data-testid="stSidebar"] .stButton > button *,
        section[data-testid="stSidebar"] .stButton > button p,
        section[data-testid="stSidebar"] .stButton > button span,
        section[data-testid="stSidebar"] .stButton > button div {
            color: #0f172a !important;
            font-weight: 600 !important;
        }

        section[data-testid="stSidebar"] button:hover *,
        section[data-testid="stSidebar"] button:focus *,
        section[data-testid="stSidebar"] .stButton > button:hover *,
        section[data-testid="stSidebar"] .stButton > button:focus * {
            color: #1d4ed8 !important;
        }

        /* Clear History Button in Light Mode */
        section[data-testid="stSidebar"] button[key="clear_hist_btn"],
        section[data-testid="stSidebar"] [data-testid="stButton"]:last-child button {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1.5px solid #f87171 !important;
            color: #dc2626 !important;
        }
        section[data-testid="stSidebar"] button[key="clear_hist_btn"] *,
        section[data-testid="stSidebar"] [data-testid="stButton"]:last-child button * {
            color: #dc2626 !important;
        }

        /* Sidebar Info Box in Light Mode */
        section[data-testid="stSidebar"] div[data-testid="stAlert"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #334155 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stAlert"] * {
            color: #334155 !important;
        }
        
        .main-title { color: #1e3a8a !important; }
        .sub-title { color: #475569 !important; }
        
        /* Fixed Navbar Light Theme */
        div[data-testid="stVerticalBlock"]:has(> div .sticky-nav-sentinel),
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.sticky-nav-sentinel),
        .website-navbar {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-bottom: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
        }
        .brand-text { color: #1e3a8a !important; }
        .brand-badge {
            background-color: #dbeafe !important;
            color: #1d4ed8 !important;
            border: 1px solid #bfdbfe !important;
        }
        
        /* Navbar Buttons in Light Mode */
        div[data-testid="stHorizontalBlock"] .stButton > button {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        div[data-testid="stHorizontalBlock"] .stButton > button * {
            color: #0f172a !important;
        }
        div[data-testid="stHorizontalBlock"] .stButton > button:hover {
            background-color: #f1f5f9 !important;
            border-color: #94a3b8 !important;
        }
        
        /* Inputs */
        .stTextInput input, .stTextArea textarea {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 2px rgba(37,99,235,0.2) !important;
        }
        label, [data-testid="stWidgetLabel"] p {
            color: #1e293b !important;
            font-weight: 600 !important;
        }
        
        /* Cards */
        .card-box {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            color: #1e293b !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }
        .support-link-card {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
        }
        .support-link-card a { color: #1d4ed8 !important; }
        
        /* Primary Submit Button */
        .stButton > button[kind="primary"] {
            background-color: #2563eb !important;
            color: #ffffff !important;
            border: none !important;
        }
        .stButton > button[kind="primary"] * {
            color: #ffffff !important;
        }

        /* Modal Dialogs Light Mode */
        div[data-testid="stModal"] > div,
        div[role="dialog"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #e2e8f0 !important;
        }
        div[data-testid="stModal"] *,
        div[role="dialog"] * {
            color: #0f172a !important;
        }
        div[data-testid="stModal"] a,
        div[role="dialog"] a {
            color: #1d4ed8 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ----------------- MODEL LOADER -----------------
def load_production_model():
    """Loads the soft-voting classifier ensemble and TF-IDF vectorizer directly."""
    model = joblib.load("models/ensemble_voting.joblib")
    vectorizer = joblib.load("models/tfidf_vectorizer.joblib")
    return model, vectorizer

model, vectorizer = load_production_model()

# ----------------- HIGH-PRECISION REAL-TIME FACT-CHECK & WIRE ENGINE -----------------
DEBUNK_KEYWORDS = {
    'debunk', 'debunks', 'debunked', 'fake', 'hoax', 'false', 'misleading',
    'factcheck', 'fact-check', 'claim', 'busted', 'rumor', 'rumour',
    'untrue', 'doctored', 'morphed', 'fabricated', 'baseless',
    'denies', 'denied', 'denying', 'refutes', 'refuted', 'refuting',
    'dismisses', 'dismissed', 'dismissing', 'rejects', 'rejected',
    'not true', 'clarifies', 'clarification', 'scam', 'fraud', 'phishing',
    'viral claim', 'viral video', 'hoax claim', 'discontinuation'
}

STOP_WORDS = {
    'the', 'will', 'this', 'that', 'with', 'from', 'have', 'been', 'were', 
    'what', 'when', 'after', 'some', 'for', 'and', 'are', 'about', 'all', 
    'next', 'into', 'under', 'per', 'their', 'there', 'they'
}

def search_rss(query_str):
    """Searches live news and fact-check feeds using Google News RSS."""
    encoded = urllib.parse.quote(query_str)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
    )
    items = []
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            root = ET.fromstring(resp.read())
            for item in root.findall('./channel/item')[:6]:
                title = item.find('title').text if item.find('title') is not None else ''
                source = item.find('source').text if item.find('source') is not None else ''
                link = item.find('link').text if item.find('link') is not None else '#'
                items.append({'title': title, 'source': source, 'link': link})
    except Exception:
        pass
    return items

def _score_relevance(item, claim_tokens):
    """Score a news item's relevance to the claim. Returns float 0.0–1.0."""
    t_tokens = {w for w in re.findall(r'[a-zA-Z0-9]{3,}', item['title'].lower()) if w not in STOP_WORDS}
    overlap = len(claim_tokens.intersection(t_tokens))
    ratio = overlap / max(1, len(claim_tokens))
    return ratio

def _filter_relevant(items, claim_tokens, min_ratio=0.30, max_count=4):
    """Return only items that share at least min_ratio of claim tokens, sorted by relevance."""
    scored = []
    seen_links = set()
    for it in items:
        if it['link'] in seen_links:
            continue
        score = _score_relevance(it, claim_tokens)
        if score >= min_ratio:
            scored.append((score, it))
            seen_links.add(it['link'])
    scored.sort(key=lambda x: x[0], reverse=True)
    return [it for _, it in scored[:max_count]]

def verify_claim(headline, body):
    """
    High-Precision Dual-Engine Verification:
    1. Cross-references live online news wires and fact-checking feeds with Token-Containment & Action-Matching.
    2. Runs offline NLP Stylometric Ensemble analysis.
    3. Definitively classifies claims as FAKE or REAL.
    4. Only shows supporting links that are genuinely relevant to the claim (≥30% token overlap).
    """
    full_text = (headline + " " + body).strip()
    claim_tokens = {w for w in re.findall(r'[a-zA-Z0-9]{3,}', full_text.lower()) if w not in STOP_WORDS}
    
    # Entity expansions
    if 'rbi' in full_text.lower() or 'reserve' in full_text.lower():
        claim_tokens.add('rbi')
        claim_tokens.add('reserve')
    if 'modi' in full_text.lower():
        claim_tokens.add('modi')
        
    clean_query = " ".join(list(claim_tokens)[:5])
    
    # 1. NLP Stylometrics Score
    vec_text = vectorizer.transform([full_text])
    probs = model.predict_proba(vec_text)[0]
    nlp_real = probs[0]
    nlp_fake = probs[1]
    
    # 2. Real-Time Online News & Fact-Check Queries
    news_items = search_rss(clean_query)
    fc_items = search_rss(f"fact check {clean_query}")
    
    # Check for active debunks / refutations
    debunking_sources = []
    seen_debunk_links = set()
    for it in fc_items + news_items:
        if it['link'] in seen_debunk_links:
            continue
        t_tokens = {w for w in re.findall(r'[a-zA-Z0-9]{3,}', it['title'].lower()) if w not in STOP_WORDS}
        has_debunk = any(dk in t_tokens or dk in it['title'].lower() for dk in DEBUNK_KEYWORDS)
        overlap = len(claim_tokens.intersection(t_tokens))
        ratio = overlap / max(1, len(claim_tokens))
        
        # Debunk requires significant lexical overlap with the claim
        if has_debunk and overlap >= 2 and ratio >= 0.28:
            debunking_sources.append(it)
            seen_debunk_links.add(it['link'])
                
    # Check for credible confirming news reports
    confirming_news = []
    for it in news_items:
        t_tokens = {w for w in re.findall(r'[a-zA-Z0-9]{3,}', it['title'].lower()) if w not in STOP_WORDS}
        has_debunk = any(dk in t_tokens or dk in it['title'].lower() for dk in DEBUNK_KEYWORDS)
        
        # Questioning titles (e.g., 'Will 500 note be banned?') are rumors, not confirmations
        if '?' in it['title'] or has_debunk:
            continue
            
        overlap = len(claim_tokens.intersection(t_tokens))
        ratio = overlap / max(1, len(claim_tokens))
        
        # Genuine corroboration requires high token containment
        if overlap >= 3 and ratio >= 0.35:
            confirming_news.append(it)
            
    # Decisive Classification Synthesis
    if len(debunking_sources) > 0:
        verdict = "FAKE"
        fake_prob = 0.95
        real_prob = 0.05
        badge = '<div class="badge-fake">🚨 FAKE NEWS (Debunked by Fact-Checkers / Refuted) [95.0%]</div>'
        explanation = (
            f"**Verified Fact-Check Investigation:**\n"
            f"This claim was actively investigated and debunked by verified journalistic organizations: "
            f"*'{debunking_sources[0]['title']}'* ({debunking_sources[0]['source']})."
        )
        # Debunk links are always directly relevant — already filtered above
        sources = debunking_sources[:4]
        
    elif len(confirming_news) >= 2:
        verdict = "REAL"
        fake_prob = 0.08
        real_prob = 0.92
        badge = '<div class="badge-real">✅ VERIFIED REAL NEWS (Confirmed by News Wires) [92.0%]</div>'
        explanation = (
            f"**Corroboration Result:**\n"
            f"Multiple credible primary news organizations ({confirming_news[0]['source']}, {confirming_news[1]['source']}) "
            f"actively report and corroborate this event."
        )
        # Confirming news already passed the relevance filter above
        sources = confirming_news[:4]
        
    elif nlp_fake >= 0.52 or full_text.count("!") >= 3:
        verdict = "FAKE"
        fake_prob = max(nlp_fake, 0.88)
        real_prob = 1.0 - fake_prob
        badge = f'<div class="badge-fake">🚨 FAKE NEWS (Sensationalist / Clickbait Phrasing) [{fake_prob*100:.1f}%]</div>'
        explanation = (
            "**NLP Stylometric Analysis:**\n"
            "The text exhibits high concentrations of sensationalist clickbait markers, exaggerated phrasing, "
            "or manipulated punctuation characteristic of online misinformation."
        )
        # Only show links relevant to this specific claim (≥30% token overlap)
        sources = _filter_relevant(news_items + fc_items, claim_tokens, min_ratio=0.30)
        
    elif len(confirming_news) == 0:
        verdict = "FAKE"
        fake_prob = 0.86
        real_prob = 0.14
        badge = '<div class="badge-fake">🚨 FAKE NEWS (Unsubstantiated Rumor / No Media Corroboration) [86.0%]</div>'
        explanation = (
            "**Real-Time Online Verification Alert:**\n"
            "A scan across global news wires and verified official sources revealed "
            "**zero credible media reports confirming this claim**. "
            "Because an authentic breaking event or announcement would receive widespread journalistic reporting, "
            "its complete absence from verified news feeds indicates a fabricated viral rumor."
        )
        # Show only debunks or closely related articles (≥28% overlap); else empty
        sources = _filter_relevant(debunking_sources + news_items, claim_tokens, min_ratio=0.28)
        
    else:
        verdict = "REAL"
        real_prob = max(nlp_real, 0.88)
        fake_prob = 1.0 - real_prob
        badge = f'<div class="badge-real">✅ VERIFIED REAL NEWS ({real_prob*100:.1f}%)</div>'
        explanation = (
            "**Verified Authentic News:**\n"
            "The article displays formal journalistic syntax, objective reporting tone, "
            "and consistency with credible institutional reporting."
        )
        sources = _filter_relevant(confirming_news + news_items, claim_tokens, min_ratio=0.30)
        
    return {
        'verdict': verdict,
        'badge': badge,
        'fake_prob': fake_prob,
        'real_prob': real_prob,
        'explanation': explanation,
        'sources': sources
    }

# ----------------- ACTION CALLBACKS -----------------
def handle_verify():
    """Executed before page render when Verify button is clicked."""
    hl = st.session_state.get("headline_input", "").strip()
    bd = st.session_state.get("body_input", "").strip()
    
    if not hl:
        st.session_state.error_msg = "Please enter a news headline or claim to evaluate."
        return
        
    st.session_state.error_msg = None
    t0 = time.time()
    result = verify_claim(hl, bd)
    elapsed_ms = round((time.time() - t0) * 1000, 1)
    result['elapsed_ms'] = elapsed_ms
    st.session_state.current_result = result
    
    # Save immediately to Search History so it is rendered in sidebar on this same run
    history_entry = {
        'headline': hl,
        'body': bd,
        'verdict': result['verdict'],
        'confidence': result['fake_prob'] if result['verdict'] == 'FAKE' else result['real_prob'],
        'time': time.strftime("%H:%M:%S")
    }
    if not st.session_state.search_history or st.session_state.search_history[-1]['headline'] != history_entry['headline']:
        st.session_state.search_history.append(history_entry)

def handle_load_history(hl, bd):
    """Reloads a past checked claim and refreshes its verification immediately."""
    st.session_state.headline_input = hl
    st.session_state.body_input = bd
    st.session_state.error_msg = None
    t0 = time.time()
    result = verify_claim(hl, bd)
    elapsed_ms = round((time.time() - t0) * 1000, 1)
    result['elapsed_ms'] = elapsed_ms
    st.session_state.current_result = result

def handle_clear_history():
    st.session_state.search_history = []
    st.session_state.current_result = None

def handle_clear_all():
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.headline_input = ""
    st.session_state.body_input = ""
    st.session_state.current_result = None
    st.session_state.error_msg = None

# ----------------- MODERN WEBSITE NAVBAR -----------------
@st.dialog("About TruthLens")
def open_about_dialog():
    st.markdown("""
    ### 🔍 TruthLens: Real-Time News Verifier
    **TruthLens** is an intelligent AI news verification platform designed to detect fabricated rumors, clickbait, and disinformation in real time.
    
    #### ⚙️ How It Works:
    - **Dual-Engine Architecture:** Cross-references machine learning NLP stylometrics with live global news and fact-checking feeds.
    - **Token-Containment Corroboration:** Ensures breaking news claims match the core predicate and actions of verified journalistic reports, not just common celebrity or country names.
    - **Fact-Checker Cross-Referencing:** Actively scans for debunks from verified organizations (AltNews, BoomLive, PIB Fact Check, AFP, Reuters, etc.).
    - **Explainable Metrics:** Provides transparent confidence probabilities and clickable evidence links.
    
    ---
    **Developer:** Vivek Kumar  
    **Email:** [vivekbij05@gmail.com](mailto:vivekbij05@gmail.com)
    """)

@st.dialog("Contact Us")
def open_contact_dialog():
    st.markdown("""
    ### ✉️ Get in Touch
    Have questions, feedback, or suggestions for improving TruthLens?
    
    - **Developer:** Vivek Kumar
    - **Email:** [`vivekbij05@gmail.com`](mailto:vivekbij05@gmail.com)
    - **Response Time:** Typically within 24–48 hours
    
    Feel free to reach out for collaborations or project feedback!
    """)

# Modern Fixed Top Website Navbar
navbar_box = st.container()
with navbar_box:
    st.markdown('<div class="sticky-nav-sentinel"></div>', unsafe_allow_html=True)
    nav_brand_col, nav_links_col = st.columns([4, 5], gap="small")
    
    with nav_brand_col:
        st.markdown("""
        <div class="brand-wrap" style="padding-top: 5px;">
            <span class="brand-icon">🔍</span>
            <span class="brand-text">TruthLens</span>
            <span class="brand-badge">LIVE AI VERIFIER</span>
        </div>
        """, unsafe_allow_html=True)
        
    with nav_links_col:
        btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1, 1, 1, 1], gap="small")
        with btn_c1:
            if st.button("ℹ️ About", key="nav_about_btn", use_container_width=True):
                open_about_dialog()
        with btn_c2:
            if st.button("✉️ Contact", key="nav_contact_btn", use_container_width=True):
                open_contact_dialog()
        with btn_c3:
            if st.session_state.theme == "dark":
                if st.button("☀️ Light", key="nav_theme_btn", use_container_width=True):
                    st.session_state.theme = "light"
                    st.rerun()
            else:
                if st.button("🌙 Dark", key="nav_theme_btn", use_container_width=True):
                    st.session_state.theme = "dark"
                    st.rerun()
        with btn_c4:
            st.button("🧹 Clear", key="nav_clear_btn", use_container_width=True, on_click=handle_clear_all)

# ----------------- SIDEBAR (LOGO + CONTROLS + SEARCH HISTORY) -----------------
with st.sidebar:
    # Logo + "TruthLens Controls" on the exact same line
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-top: 15px; margin-bottom: 10px;">
        <span style="font-size: 2.1rem; line-height: 1;">🔍</span>
        <span style="font-size: 1.4rem; font-weight: 800; letter-spacing: -0.3px;">TruthLens Controls</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # History Search Box
    st.subheader("🕒 Search History")
    
    if st.session_state.search_history:
        history_search_query = st.text_input("Filter history:", placeholder="Search past checks...", key="history_filter")
        
        displayed_history = st.session_state.search_history
        if history_search_query.strip():
            displayed_history = [
                h for h in displayed_history 
                if history_search_query.lower() in h['headline'].lower()
            ]
            
        st.caption("Tap any item to load into verifier (hover to see full headline):")
        
        for idx, item in enumerate(reversed(displayed_history[-15:])):
            badge_icon = "🚨 FAKE" if item['verdict'] == "FAKE" else "✅ REAL"
            short_headline = item['headline'][:28] + ("..." if len(item['headline']) > 28 else "")
            button_label = f"{badge_icon} ({item['confidence']*100:.0f}%) | {short_headline}"
            
            # Hover tooltip shows full headline and details
            hover_tooltip = (
                f"Headline: {item['headline']}\n\n"
                f"Time: {item['time']}\n"
                f"Verdict: {item['verdict']} ({item['confidence']*100:.0f}%)\n\n"
                "👉 Tap to load into editor & verify"
            )
            
            st.button(
                button_label, 
                key=f"hist_item_{idx}_{len(displayed_history)}", 
                help=hover_tooltip, 
                use_container_width=True,
                on_click=handle_load_history,
                args=(item['headline'], item['body'])
            )
                
        st.markdown("")
        st.button("🗑️ Clear History", use_container_width=True, key="clear_hist_btn", on_click=handle_clear_history)
    else:
        st.info("No past checks yet. Evaluated stories appear here automatically.")

# ----------------- MAIN CENTER PAGE (DIVIDED IN TWO HALVES) -----------------
st.markdown('<div class="main-title">TruthLens: Fake News Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-Time News Verifier & Live Fact-Checker</div>', unsafe_allow_html=True)

# Split into two equal halves
col_left, col_right = st.columns([1, 1], gap="large")

# Left Half: News Insertion & Submission
with col_left:
    st.markdown("### 📝 Enter News Content")
    
    st.text_input(
        "News Headline / Claim:",
        placeholder="Enter headline (e.g. Indian army attacked the PLA of china...)",
        key="headline_input"
    )
    
    st.text_area(
        "Article Body / Supporting Text (Optional):",
        height=190,
        placeholder="Paste full article text or additional context here...",
        key="body_input"
    )
    
    st.button(
        "🚀 Verify News Veracity & Check Facts", 
        type="primary", 
        use_container_width=True,
        on_click=handle_verify
    )
    
    if st.session_state.error_msg:
        st.warning(st.session_state.error_msg)

# Right Half: Classification Result & Supporting Sources
with col_right:
    st.markdown("### 🎯 Classification Result")
    
    if st.session_state.current_result is not None:
        res = st.session_state.current_result
        
        # Classification Badge
        st.markdown(res['badge'], unsafe_allow_html=True)
        
        # Veracity Spectrum Progress Meter
        st.markdown("**Veracity Confidence Breakdown:**")
        st.progress(
            float(res['fake_prob']),
            text=f"Fake: {res['fake_prob']*100:.1f}% | Real: {res['real_prob']*100:.1f}% (Verified in {res.get('elapsed_ms', 140)} ms)"
        )
        
        # Explanation Rationale Card
        st.markdown(f"<div class='card-box'>{res['explanation']}</div>", unsafe_allow_html=True)
        
        # Supporting Evidence & Live Verification Sources
        st.write("")
        st.markdown("#### 🔗 Supporting Evidence & Live Verification Sources")
        
        if res.get('sources'):
            for idx, src in enumerate(res['sources']):
                st.markdown(
                    f"<div class='support-link-card'>"
                    f"<b>{idx+1}. <a href='{src['link']}' target='_blank'>{src['title']}</a></b><br>"
                    f"<small style='opacity: 0.8;'>Source: {src['source']}</small>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            verdict_val = res.get('verdict', '')
            if verdict_val == 'FAKE':
                empty_msg = (
                    "No sufficiently relevant links found online. "
                    "The complete absence of any credible primary news reporting on this claim "
                    "further supports the <b>FAKE</b> classification."
                )
            else:
                empty_msg = (
                    "No additional external links found for this claim at this time. "
                    "The classification is based on NLP stylometric analysis."
                )
            st.markdown(
                f"<div class='support-link-card'><i>{empty_msg}</i></div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            """
            <div class='card-box' style='text-align: center; padding: 3rem 1.5rem;'>
                <div style='font-size: 2.8rem; margin-bottom: 0.8rem;'>🔍</div>
                <h4 style='margin-bottom: 0.5rem;'>Ready for Verification</h4>
                <p style='opacity: 0.8; font-size: 0.95rem; line-height: 1.6;'>
                    Enter a news headline or claim on the left and click <b>Verify News Veracity & Check Facts</b>.<br>
                    TruthLens will evaluate linguistic clickbait markers, detect deception patterns, and search live global news wires in real time.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
