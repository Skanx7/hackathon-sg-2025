import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROXY_AUTH : str = os.getenv("PROXY_AUTH", "")
    PROXY_URL : str = os.getenv("PROXY_URL", "")
    
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "cac40_sentiment")


    SQL_URL : str = os.getenv("SQL_URL", "mysql://root:@localhost:3306")
    SQL_DB : str = os.getenv("SQL_DB", "hackathon")
    SQLITE_URL: str = os.getenv("SQLITE_URL", "sqlite:///./cac40_prices.db")

    NEWS_API_URL: str = os.getenv("NEWS_API_URL", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

    POLYGON_API_URL: str = os.getenv("POLYGON_API_URL", "")
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")

    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "CAC40SentimentBot/1.0")

    CAC40_TICKERS = {
        "AIR.PA":   {"ticker": "AIR.PA",   "name": "Airbus",                  "alternate_ticker": "EADSY"},
        "ALO.PA":   {"ticker": "ALO.PA",   "name": "Alstom",                  "alternate_ticker": "ALSMY"},
        "MT.AS":    {"ticker": "MT.AS",    "name": "ArcelorMittal",           "alternate_ticker": "MT"},
        "CS.PA":    {"ticker": "CS.PA",    "name": "AXA",                     "alternate_ticker": "AXAHY"},
        "BNP.PA":   {"ticker": "BNP.PA",   "name": "BNP Paribas",             "alternate_ticker": "BNPQY"},
        "EN.PA":    {"ticker": "EN.PA",    "name": "Bouygues",                "alternate_ticker": "BOUYY"},
        "CAP.PA":   {"ticker": "CAP.PA",   "name": "Capgemini",               "alternate_ticker": "CGEMY"},
        "CA.PA":    {"ticker": "CA.PA",    "name": "Carrefour",               "alternate_ticker": "CRRFY"},
        "ACA.PA":   {"ticker": "ACA.PA",   "name": "Crédit Agricole",         "alternate_ticker": "CRARY"},
        "BN.PA":    {"ticker": "BN.PA",    "name": "Danone",                  "alternate_ticker": "DANOY"},
        "DSY.PA":   {"ticker": "DSY.PA",   "name": "Dassault Systèmes",       "alternate_ticker": "DASTY"},
        "ENGI.PA":  {"ticker": "ENGI.PA",  "name": "Engie",                   "alternate_ticker": "ENGIY"},
        "EL.PA":    {"ticker": "EL.PA",    "name": "EssilorLuxottica",        "alternate_ticker": "ESLOY"},
        "ERF.PA":   {"ticker": "ERF.PA",   "name": "Eramet",                  "alternate_ticker": "ERMAY"},
        "RMS.PA":   {"ticker": "RMS.PA",   "name": "Hermès",                  "alternate_ticker": "HESAY"},
        "KER.PA":   {"ticker": "KER.PA",   "name": "Kering",                  "alternate_ticker": "PPRUY"},
        "LR.PA":    {"ticker": "LR.PA",    "name": "Legrand",                 "alternate_ticker": "LGRDY"},
        "OR.PA":    {"ticker": "OR.PA",    "name": "L'Oréal",                 "alternate_ticker": "LRLCY"},
        "MC.PA":    {"ticker": "MC.PA",    "name": "LVMH",                    "alternate_ticker": "LVMUY"},
        "ML.PA":    {"ticker": "ML.PA",    "name": "Michelin",                "alternate_ticker": "MGDDY"},
        "ORA.PA":   {"ticker": "ORA.PA",   "name": "Orange",                  "alternate_ticker": "ORANY"},
        "RI.PA":    {"ticker": "RI.PA",    "name": "Pernod Ricard",           "alternate_ticker": "PDRDY"},
        "PUB.PA":   {"ticker": "PUB.PA",   "name": "Publicis",                "alternate_ticker": "PUBGY"},
        "RNO.PA":   {"ticker": "RNO.PA",   "name": "Renault",                 "alternate_ticker": "RNLSY"},
        "SAF.PA":   {"ticker": "SAF.PA",   "name": "Safran",                  "alternate_ticker": "SAFRY"},
        "SGO.PA":   {"ticker": "SGO.PA",   "name": "Saint-Gobain",            "alternate_ticker": "CODYY"},
        "SAN.PA":   {"ticker": "SAN.PA",   "name": "Sanofi",                  "alternate_ticker": "SNY"},
        "SU.PA":    {"ticker": "SU.PA",    "name": "Schneider Electric",      "alternate_ticker": "SBGSY"},
        "GLE.PA":   {"ticker": "GLE.PA",   "name": "Société Générale",        "alternate_ticker": "SCGLY"},
        "STLAP.PA": {"ticker": "STLAP.PA", "name": "Stellantis",              "alternate_ticker": "STLA"},
        "STMPA.PA": {"ticker": "STMPA.PA", "name": "STMicroelectronics",      "alternate_ticker": "STM"},
        "TEP.PA":   {"ticker": "TEP.PA",   "name": "Teleperformance",         "alternate_ticker": "TLPFY"},
        "HO.PA":    {"ticker": "HO.PA",    "name": "Thales",                  "alternate_ticker": "THLLY"},
        "TTE.PA":   {"ticker": "TTE.PA",   "name": "TotalEnergies",           "alternate_ticker": "TTE"},
        "URW.PA":   {"ticker": "URW.PA",   "name": "Unibail-Rodamco-Westfield","alternate_ticker": "URMCY"},
        "VIE.PA":   {"ticker": "VIE.PA",   "name": "Veolia",                  "alternate_ticker": "VEOEY"},
        "DG.PA":    {"ticker": "DG.PA",    "name": "Vinci",                   "alternate_ticker": "VCISY"},
        "VIV.PA":   {"ticker": "VIV.PA",   "name": "Vivendi",                 "alternate_ticker": "VIVHY"},
        "WLN.PA":   {"ticker": "WLN.PA",   "name": "Worldline",               "alternate_ticker": "WRDLY"},
    }
    CACHE_DIR = os.getenv("CACHE_DIR", None)
    FINANCE_MODEL = "ProsusAI/finbert" 


settings = Settings()