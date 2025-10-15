# -*- coding: utf-8 -*-
import json, re, unicodedata
from collections import defaultdict

INPUT = "data/grp11_combined_cookie_knowledgebase.json"
OUTPUT = "data/ingredient_classes.auto.json"

# INPUT = "data/test_base.json"
# OUTPUT = "data/test_ingredient_classes.auto.json"

# ---- 1)  ----
def normalize_name(name: str) -> str:
    s = name.strip().lower()
    s = unicodedata.normalize("NFKC", s)
    # remove descriptors
    drop_words = [
        r"\bunsalted\b", r"\bsalted\b", r"\bsoftened\b", r"\bmelted\b", r"\bsoft\b",
        r"\broom temperature\b", r"\bcold\b", r"\bwarm\b", r"\bfine\b", r"\bgranulated\b",
        r"\bcaster\b", r"\bicing\b", r"\bpowdered\b", r"\bconfectioners'?s?\b",
        r"\bdark\b", r"\blight\b", r"\bwhite\b", r"\bbrown\b"
    ]
    for w in drop_words:
        s = re.sub(w, "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# ---- 2) key wo ----
# pattern, set of classes
KEYWORDS = [
    # flour / starch
    (r"\b(flour|cake flour|all[- ]purpose|ap flour|plain flour|bread flour|cornstarch|corn starch|starch)\b", {"flour"}),
    # sugars / syrups
    (r"\b(sugar|caster sugar|brown sugar|demerara|turbinado|jaggery)\b", {"sweet"}),
    (r"\b(honey|maple syrup|golden syrup|corn syrup|agave)\b", {"sweet","liquid"}),
    # fats
    (r"\b(butter|ghee|shortening|lard)\b", {"fat"}),
    (r"\b(oil|olive oil|vegetable oil|canola|sunflower|coconut oil)\b", {"fat"}),
    # eggs / binders
    (r"\b(egg|egg yolk|yolk|egg white|albumen|aquafaba)\b", {"binder","liquid"}),
    # liquids (dairy & others)
    (r"\b(milk|whole milk|buttermilk|evaporated milk|condensed milk|cream|double cream|heavy cream|half[- ]and[- ]half|yogurt|kefir|sour cream)\b", {"liquid","dairy"}),
    (r"\b(water)\b", {"liquid"}),
    # chocolate & cocoa
    (r"\b(cocoa|cacao powder|cocoa powder)\b", {"inclusion","cocoa","bitter"}),
    (r"\b(chocolate|choc|chocolate chips|choc chips|cacao nibs|chocolate chunks|chips|nibs)\b", {"inclusion","sweet"}),
    # leavening
    (r"\b(baking powder|baking soda|bicarbonate|yeast)\b", {"leavening"}),
    # salt
    (r"\b(salt|kosher salt|sea salt|table salt|fleur de sel)\b", {"salt"}),
    # spices & aromatics
    (r"\b(cinnamon|nutmeg|ginger|clove|cloves|cardamom|allspice|anise|star anise|mace)\b", {"spice","aroma"}),
    (r"\b(vanilla|vanilla extract|vanilla bean|vanillin)\b", {"aroma","sweet"}),
    (r"\b(espresso|coffee)\b", {"aroma","bitter"}),
    (r"\b(rose water|orange blossom|almond extract|lemon extract)\b", {"aroma"}),
    # citrus / acid
    (r"\b(lemon|lime|orange|zest|lemon zest|orange zest|lemon juice|lime juice)\b", {"aroma","acid"}),
    # nuts / seeds / dried fruit
    (r"\b(almond|hazelnut|pecan|walnut|pistachio|macadamia|peanut)\b", {"inclusion","nut"}),
    (r"\b(sesame|poppy seed|chia|linseed|flaxseed)\b", {"inclusion","seed"}),
    (r"\b(raisin|sultana|currant|cranberry|dried fruit|apricot|date|fig)\b", {"inclusion","fruit"}),
    # miso / tahini / biscoff / spreads
    (r"\b(miso)\b", {"seasoning","umami","savoury"}),
    (r"\b(tahini|sesame paste)\b", {"fat","inclusion","seed"}),
    (r"\b(biscoff|cookie butter|speculoos)\b", {"sweet","inclusion","spread"}),
    # other
    (r"\b(oats?|rolled oats?|instant oats?)\b", {"grain","inclusion"}),
    (r"\b(cornflour)\b", {"flour"}),
]

# synonyms / aliases
ALIASES = {
    "ap flour": "all-purpose flour",
    "plain flour": "all-purpose flour",
    "caster sugar": "granulated sugar",
    "powdered sugar": "icing sugar",
    "confectioners sugar": "icing sugar",
    "bicarbonate of soda": "baking soda",
}

def infer_classes(name_raw: str) -> set:
    name = normalize_name(name_raw)
    # alias
    if name in ALIASES:
        name = ALIASES[name]
    tags = set()
    for pattern, cls in KEYWORDS:
        if re.search(pattern, name):
            tags |= cls
    return tags

# ---- 3)  ----
with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

recipes = data.get("recipes", [])
ingredients_set = set()
for r in recipes:
    for ing in r.get("ingredients", []):
        ingredients_set.add(ing.get("ingredient", "").strip())

classes = {}
unlabeled = []
for ing in sorted(ingredients_set, key=lambda x: x.lower()):
    inferred = infer_classes(ing)
    classes[ing] = sorted(list(inferred))  # store as sorted list for consistency
    if not inferred:
        unlabeled.append(ing)

# save to file
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(classes, f, indent=2, ensure_ascii=False)

print(f"✅ Saved auto classes to: {OUTPUT}")
print(f"Total unique ingredients: {len(classes)}")
print(f"Labeled by rules: {len(classes) - len(unlabeled)}")
print(f"Unlabeled (need review): {len(unlabeled)}")

if unlabeled:
    print("\nUnlabeled examples (first 30):")
    for name in unlabeled[:30]:
        print(" -", name)
