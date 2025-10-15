# 🍪 Genetic Recipe Generator & Mini Cookbook

### 1.Overview
This project evolves cookie recipes using a Genetic Algorithm (GA) guided by an Inspiring Set Knowledgebase.
Outputs are presented by front end and rendered into a small cookbook (PDF), clearly marking AI-generated parts and including a reflection on AI use.

### 2.Repository Structure
```
Recipebook/
  images/                # pictures used by the cookbook pages
  cookbook.pdf           # merged one-file cookbook (final deliverable)
  index.html             
  recipe_241.html        
  recipe_242.html       
  recipe_243.html       
  style.css              # shared styles (media="all" for print & screen)
knowledgeBase/           # inspiring set JSON, ingredient lists, etc.
results/                 # GA run outputs, intermediate JSON, plots
.gitattributes
README.md
findout_of_results.ipynb # analysis / visualization notebook (optional)
```

### 3.📚 Knowledgebase (Inspiring Set)
What's in this folder?
```
knowledgeBase/
  grp11_37_cookie_knowledgebase.json
  grp11_37_cookies_recipes.json
  grp11_62_cookie_knowledgebase.json
  grp11_62_cookies_recipes.json
  grp11_combined_cookie_knowledgebase.json
  grp11_combined_cookies_knowledgebase.json
```
+ *_cookies_recipes.json: Raw recipe records scraped/cleaned from the source site(s). Includes title, ingredients (name/qty/unit), steps, and bake info.

+ *_cookie_knowledgebase.json: Enriched knowledgebase derived from the raw recipes—adds ingredient classes (e.g., fat/flour/sugar/liquid/spice), roles (binding/rising/tenderizer/seasoning/decoration), constraints (min/max/step), and tags (type/course/flavor/diet).

+ grp11_combined_*: De-duplicated merged sets (e.g., combining the 37-item and 62-item batches) to use as the default inspiring set for experiments.

> The numbers (e.g., 37, 62) indicate the batch size of collected recipes, which helps with provenance and A/B comparisons.

### 4.⚙️ Recipe Generator (Python, Genetic Algorithm)
This module evolves cookie/cake recipes using a Genetic Algorithm (GA) guided by the inspiring set knowledgebase.
```
computational creativity recipe ge…/
└─ code/
   ├─ data/
   │  └─ inspring_set_classes.py   # ingredient classes, roles, constraints, tag vocab (typo in name is fine)
   ├─ recipe_generator.py          # GA entry point (run from CLI)
└─ results/                        # GA outputs (runs, logs, top-K recipes)
```

What it does?

1.Loads an enriched knowledgebase (ingredients + roles + constraints + inspiring recipes).

2.Encodes a candidate recipe as a fixed-length genome (key groups: fat/flour/sugar/binder/liquid/leavening/salt/mix-ins + bake settings).

3.Evolves a population with selection → crossover → mutation.

4.Scores candidates with a multi-term fitness (ratios/feasibility/style/diversity).

5.Emits the best K recipes and run artifacts into results/.

