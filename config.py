# ============================================================
# config.py — Central configuration for the lead gen scraper
# ============================================================
# STRATEGY FOR 1000 LEADS:
#   Google Maps caps results at ~120 per query.
#   Running 12 diverse queries = 1000–1400 unique leads.
#   Each query targets a different business category or Delhi area.
# ============================================================

# --- Search Queries (12 categories × ~100 results = ~1000–1200 leads) ---
SEARCH_QUERIES = [
    # Cafes & Restaurants
    "cafes in Connaught Place Delhi",
    "restaurants in Hauz Khas Delhi",
    "restaurants in Lajpat Nagar Delhi",
    "restaurants in Karol Bagh Delhi",
    # Gyms & Wellness
    "gyms in Delhi",
    "yoga centers in Delhi",
    # Salons & Spas
    "beauty salons in Delhi",
    "spas in Delhi",
    # Retail & Services
    "boutiques in Saket Delhi",
    "coaching centers in Delhi",
    # Healthcare
    "dental clinics in Delhi",
    "physiotherapy clinics in Delhi",
]

# Maximum number of results to collect PER QUERY
# 12 queries × 100 = up to 1,200 (after dedup expect ~1,000 unique)
MAX_RESULTS_PER_QUERY = 100

# Kept for backward CLI compatibility (--max flag)
MAX_RESULTS = MAX_RESULTS_PER_QUERY

# Output file name
OUTPUT_FILE = "delhi_leads.xlsx"

# --- Browser Configuration ---
HEADLESS = False           # Set True to run invisibly (less safe for anti-detection)
BROWSER_SLOW_MO = 30       # ms delay between Playwright actions

# --- Delay Configuration (seconds) ---
MIN_DELAY = 1.5            # Minimum random sleep between actions
MAX_DELAY = 3.5            # Maximum random sleep between actions
SCROLL_DELAY_MIN = 0.8     # Min delay between scroll steps
SCROLL_DELAY_MAX = 2.0     # Max delay between scroll steps

# --- Scrolling Configuration ---
SCROLL_STEPS = 15          # More steps = more listings loaded per cycle
SCROLL_AMOUNT = 500        # Pixels per scroll step

# --- Extraction ---
MAX_SCROLL_CYCLES = 25     # Max scroll-extract cycles per query before moving on

# --- Lead Scoring Thresholds ---
HIGH_RATING_THRESHOLD = 4.0

# --- Local Business Filter ---
# Skip any listing whose name contains these keywords (case-insensitive)
# Covers 250+ Indian & international franchise brands across all sectors
BRAND_BLACKLIST = {
    # Malls & large retail spaces
    "mall", "dlf", "select citywalk", "ambience", "pacific", "vegas",
    "unity", "mgf", "ansal", "promenade", "city centre",

    # QSR — International
    "starbucks", "mcdonald", "kfc", "subway", "domino", "pizza hut",
    "burger king", "tim hortons", "baskin robbins", "baskin-robbins",
    "taco bell", "wendy's", "wendys", "krispy kreme", "albaik",
    "papa john's", "papa johns", "popeyes",

    # QSR — National & Regional
    "cafe coffee day", "ccd", "barista", "costa coffee",
    "haldiram", "bikanervala", "wow momo", "punjab grill",
    "mainland china", "barbeque nation", "the beer cafe",
    "social", "the irish house", "hard rock",
    "adigas", "kake di hatti", "chai sutta bar",
    "tandooriwala", "goli vada pav", "lassi shop",
    "hocco", "amul", "patanjali", "kathi junction",
    "laziz pizza", "aachi masala", "monginis", "ws bakers",
    "nandini dairy", "atul bakery", "g-fresh mart",
    "behrouz biryani", "oven story", "fasoos", "faasos", "rebel foods",
    "drunken monkey", "keventers", "jumboking", "berco's", "bercos",
    "kamat's", "moti mahal", "saravana bhavan",
    "the belgian waffle", "la pino", "tealogy",
    "burgrill", "ministry of beer", "ironhill",
    "burger singh", "barcelos", "doner shack", "absolute shawarma",
    "amritsari express", "nirula's", "niru", "sagar ratna", "sankalp",
    "rolls mania", "mr idli", "kouzina", "karim's",
    "punjabi chaap corner",
    "biggies burger", "indiyana pizza", "gulf bites", "quikshef",
    "baap of rolls", "biryani by kilo", "one bite", "instabite",
    "urban desi chaat", "nawabi kukkad", "ss combo kitchen",
    "chharvi foods", "scf taste the fusion",
    "spartan qsr", "boss of burgers", "bolly bites", "rollacosta",
    "cure foods", "farzi cafe", "rowdy cafe",
    "chaat puchka", "p4pakodi", "doner & gyros",
    # Cafe & beverage chains
    "chai point", "chaayos", "kongsi tea", "yewale", "amruttulya",
    "urban theka", "theka coffee", "third wave coffee",
    "blue tokai", "di bella coffee", "kiosk kaffee", "papparoti",
    "the coffee bean", "tea leaf", "rameshwaram cafe",
    "indian coffee house", "karupatti coffee", "irani cafe",
    "t4 cafe", "tea adda", "tea avenue", "tea max cafe",
    "the tea factory", "happi tea", "chai bunk",
    "zorko", "coffeecana", "brewtopia", "bean here",
    "ajay's cafe", "cafe chocolicious", "cafe frespresso",
    "natuf cafe", "sutocafe", "unique brew cafe",
    "pokket cafe", "slay coffee", "mikel coffee",
    "the chocolate room", "brewers cafe", "jam street cafe",
    "kumbakonam coffee", "cafe durga", "ferguson plarre",
    "momizu house cafe", "rock gilis coffee",
    "coffee culture", "the coffeeshop company", "cinnzeo",
    "beyond temptation cafe", "chocolaty chai cafe",
    "momo magic cafe", "uncle peter's pancakes",

    # Fitness / Gym / Yoga chains
    "cult.fit", "cult fit", "anytime fitness", "gold's gym", "golds gym",
    "snap fitness", "talwalkars", "fitness first", "f45 training", "f45",
    "o2 gym", "aayana yoga", "the yoga institute",
    "chisel fitness", "chisel gym", "crunch fitness", "fitnessone",
    "nitrro fitness", "orangetheory", "body building india",
    "aikya yoga", "anahata yoga", "sadhana yoga", "skm yoga",
    "yogasix", "yog tree",
    "plus fitness", "jetts fitness", "easygym", "cyclebar",
    "core fitness station", "ufc gym", "energie fitness", "vivafit",
    "the gym health planet", "ozone wellness",
    "bikram yoga", "corepower yoga", "aayana yoga academy",
    "indian federation of yoga",
    "slam fitness studio", "jazzercise", "fit4mom", "9round kickboxing",

    # Salon / Spa chains
    "lakme", "jawed habib", "toni and guy", "toni & guy",
    "l'oreal", "loreal", "ylg", "o2 spa", "enrich", "green trends",
    "bodycraft salon", "looks salon", "naturals salon", "vlcc",
    "geetanjali salon", "studio11 salon", "studio 11", "studie'o 7",
    "truefitt & hill", "truefitt and hill", "shahnaz husain",
    "blossom kochhar", "aroma magic", "leisure spa",
    "athenian salon", "black velvet spa", "manea the salon",
    "moh spa", "nowmi salon", "play salon",
    "sunway wellness", "trimy tones",
    "k3 salon", "shades of black salon", "jcb salon", "spa palace",
    "beu salons", "la coiffure", "the bombay nail company",
    "trimx men's salon", "juice salon", "vantha vettuvom",
    "dabur newu salon", "newu salon", "saber salon",

    # Hotel chains
    "marriott", "hilton", "hyatt", "taj ", "oberoi", "itc hotel",
    "radisson", "sheraton", "leela", "ibis", "holiday inn",
    "novotel", "crowne plaza", "lemon tree", "oyo rooms",

    # Healthcare / Diagnostics / Pharmacy
    "apollo", "fortis", "max hospital", "aiims", "medanta",
    "dr lal pathlabs", "lal pathlabs", "wellness forever",
    "dr batra's", "dr. batra", "nephroplus", "shalby hospital",
    "pharmeasy", "generic aadhar", "oliva skin",
    # Dental chains
    "clove dental", "sabka dentist", "mydentist", "care dental",
    "dentzz", "neem tree dental", "dentistree", "smile in hour",
    "apollo dental", "dezy", "smiles.ai", "dentafix",
    "noble dental", "smile 4 sure", "smile dental pvt",
    "aj dental group", "city dental centre", "vi scan diagnostic",
    "simpladent",
    # Physiotherapy chains
    "reliva", "nonstop physio", "rewin health", "health focus physio",
    "alexa healthcare", "vlcc physiotherapy",
    "curenow wellness", "maana health", "physioentrust", "velocity physio",
    "physio care by ebg", "ebg group",
    "physioconnect", "dr. vora's physiotherapy", "dr vora physio",

    # Retail / Apparel / Fashion — International
    "adidas", "nike", "reebok", "us polo", "van heusen",
    "allen solly", "peter england", "john players", "lee cooper",
    "hush puppies", "relaxo", "khadims", "trends footwear",
    "jockey", "7-eleven", "7eleven", "zara", "miniso",
    "hamleys", "crossword",

    # Retail / Apparel / Fashion — National
    "reliance retail", "reliance trends", "jiomart", "zivame",
    "zudio", "croma", "tanishq", "westside", "lenskart",
    "firstcry", "raymond", "kalyan jewellers", "bata",
    "aurelia", "biba", "fabindia", "go colors", "manyavar",
    "sabhyata", "madame", "house of masaba",
    "global desi", "w for woman", "shree the clothing",
    "caratlane", "mia by tanishq", "kisna", "kushals", "indriya",
    "pepperfry", "royal oak", "godrej interio", "nilkamal",
    "skinlab", "cotton culture", "dtdc", "delhivery",
    "being human", "bewakoof", "the souled store", "snitch",
    "neeru's emporio", "laabha", "richlook", "siyaram",
    "ajmera fashion", "ajmera trends", "aramya", "vastranand",
    "duke", "suti", "chique",
    "jaipur kurti", "amaiva", "kesaria bazaar",

    # Tata group
    "tata ",

    # Education / Coaching chains
    "kidzee", "poly kids", "eurokids", "lighthouse learning",
    "t.i.m.e.", "time institute", "unacademy", "dale carnegie",
    "brain checker", "aakash institute", "aakash",
    "allen career", "career launcher", "fiitjee", "henry harvin",
    "byju's", "byjus", "vedantu", "kumon", "aloha",
    "avision institute", "boston institute of analytics",
    "edify schools", "eduwatts", "ibt institute",
    "kodakco", "law prep tutorial", "makoons",
    "podar education", "prerna education", "abacus trainer",
    "crack academy", "edugorilla", "brainywood", "vision30 class",
    "takshila coaching", "excel acadamics",
    "aptech", "dmit labs", "arena multimedia", "algorithmics",
    "coding giants", "baby brain", "mathnasium", "eye level",

    # Automotive / EV
    "ather energy", "ola electric", "mahindra first choice",
    "bosch car service", "carzspa", "autozspa", "the detailing mafia",

    # Logistics / Q-commerce
    "blinkit", "zepto",

    # Travel / Entertainment
    "easemytrip", "makemytrip", "thomas cook", "pvr ", "inox",

    # Wellness / Lifestyle
    "the pilates studio", "heads up for tails",
    "ferns n petals", "nykaa", "u clean",

    # Home / Electronics
    "birla opus", "ttk prestige", "pigeon appliance",
}

# --- Platform Domains (Considered "No Personal Website") ---
# Links to these domains are treated as if the business doesn't have its own site.
PLATFORM_DOMAINS = [
    "zomato.com", "zoma.to", "swiggy.com", "swig.gy", "facebook.com", "fb.com", "fb.watch",
    "instagram.com", "instagr.am", "magicpin.in", "justdial.com", "tripadvisor.com",
    "yelp.com", "youtube.com", "youtu.be", "twitter.com", "x.com", "t.co", "linkedin.com",
    "linktr.ee", "bit.ly", "tinyurl.com"
]

# Reviews upper limit — big chains have thousands, local businesses stay under this
MAX_REVIEWS_FOR_LOCAL = 1000   # ← changed from 2000 to 1000

# Skip leads that don't have a phone number (contact details)
REQUIRE_PHONE_NUMBER = True

# --- Logging ---
LOG_LEVEL = "INFO"
LOG_FILE = "scraper.log"

# --- Database & Stealth Configuration ---
DB_PATH = "leads.db"
STEALTH_ENABLED = True

# Rotate through these user agents to reduce bot signature
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"
]

