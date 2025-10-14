# 🍪 Genetic Recipe Generator & Mini Cookbook

### 1.Overview
This project evolves cookie recipes using a Genetic Algorithm (GA) guided by an Inspiring Set Knowledgebase.
Outputs are presented by front end and rendered into a small cookbook (PDF), clearly marking AI-generated parts and including a reflection on AI use.

### 2.Repository Structure
```
Recipebook/
  images/                # pictures used by the cookbook pages
  cookbook.pdf           # merged one-file cookbook (final deliverable)
  index.html             # cover + TOC + AI attribution + reflection
  recipe_241.html        # generated recipe 1 (keeps your style)
  recipe_242.html        # generated recipe 2
  recipe_243.html        # generated recipe 3
  style.css              # shared styles (media="all" for print & screen)
knowledgeBase/           # inspiring set JSON, ingredient lists, etc.
results/                 # GA run outputs, intermediate JSON, plots
.gitattributes
README.md
findout_of_results.ipynb # analysis / visualization notebook (optional)
```


