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

### 📚 Knowledgebase (Inspiring Set)
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


