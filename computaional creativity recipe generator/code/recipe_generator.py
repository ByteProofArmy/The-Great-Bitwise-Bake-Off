
# -*- coding: utf-8 -*-


import json
import pprint
import random
import math
import copy
from fractions import Fraction


with open('data/grp11_combined_cookie_knowledgebase.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

recipes = data['recipes']

UNIT_TO_ML = {
    "tsp": 5, "teaspoon": 5, "teaspoons": 5,
    "tbsp": 15, "tablespoon": 15, "tablespoons": 15,
    "cup": 240, "cups": 240,
    "ml": 1
}
UNIT_TO_G = {"g": 1, "gram": 1, "grams": 1, "kg": 1000}

DENSITY_G_PER_ML = {
    "liquid": 1.00,
    "fat": 0.91,
    "sweet": 0.85,
    "flour": 0.53,
    "inclusion": 0.70,
    "leavening": 0.90,
    "salt": 1.20,
    "default": 0.80
}

COUNT_TO_G = {
    "egg": 50,  # average egg weight 50g
}

def parse_amount(a):
    """
    takes a string or number and returns a float
    """
    if isinstance(a, (int, float)):
        return float(a)
    a = a.strip()
    # convert mixed numbers like "1 1/2"
    if " " in a:
        parts = a.split()
        if len(parts) == 2:
            return float(Fraction(parts[0])) + float(Fraction(parts[1]))
    # convert fractions like "1/2"
    if "/" in a:
        return float(Fraction(a))
    # int/float
    try:
        return float(a)
    except ValueError:
        return 0.0


def amount_in_grams(ing, tags_fn):
    """
    convert amount in given unit to grams, using tags to determine density if needed
    """

    name = ing.get("ingredient","").lower().strip()
    unit = (ing.get("unit") or "").lower().strip()
    amt = parse_amount(ing.get("amount",0))

    # g/kg
    if unit in UNIT_TO_G:
        return amt * UNIT_TO_G[unit]

    # volume -> ml -> density - > g   
    if unit in UNIT_TO_ML:
        ml = amt * UNIT_TO_ML[unit]
        tags = tags_fn(name) or set()
        for key in ["liquid","fat","sweet","flour","inclusion","leavening","salt"]:
            if key in tags:
                dens = DENSITY_G_PER_ML[key]; break
        else:
            dens = DENSITY_G_PER_ML["default"]
        return ml * dens

    # egg 
    if "egg" in name:
        return amt * COUNT_TO_G["egg"]

    # unknown unit, return amount as is (assumed to be grams)
    return amt

for r in recipes:
    for i in r['ingredients']:
        i['amount'] = parse_amount(i['amount'])

"""## Loading the Inspiring Set

"""


with open('data/ingredient_classes.auto.json', 'r', encoding='utf-8') as f:
    CLASSES = json.load(f)
    CLASSES = {k: set(v) for k, v in CLASSES.items()}

def tags(n): return CLASSES.get(n.lower(), set())



"""To check what we have loaded we can use the pretty printing library (pprint)."""

pprint.PrettyPrinter(indent=2, depth=3).pprint(recipes[0])

"""Next we extract all of the ingredients from the recipes, so that we can use them in mutation operators."""

all_ingredients = []
for recipe in recipes:
  all_ingredients.extend(recipe['ingredients'])

"""To check on the complete list of ingredients, we can use the pprint library to provide formatted list."""

pprint.PrettyPrinter(indent=2, depth=2).pprint(all_ingredients)

"""## Creating an Initial Population

Now we can create an initial population, by first defining the population size and then selecting from the list of recipes.
"""

population_size = 30

population = random.choices(recipes, k=population_size)

"""And we can check on the recipes that were selected in the initial population."""

# pprint.PrettyPrinter(indent=2, depth=2).pprint(population)

"""## Evaluating Recipes (Fitness Function)

The following function defines how individuals are evaluated:
"""

def evaluate_recipes(recipes):
  for r in recipes:
    r['fitness'] = fitness(r)


def novelty_score(r, inspiring_set):
    names_r = {i["ingredient"].lower() for i in r["ingredients"]}
    if not names_r:
        return 0.0
    max_sim = 0.0
    # compute similarity to each recipe in the inspiring set
    for base in inspiring_set:
        names_b = {i["ingredient"].lower() for i in base["ingredients"]}
        inter = len(names_r & names_b)
        union = len(names_r | names_b)
        sim = inter / union if union else 0.0
        max_sim = max(max_sim, sim)
    # novelty = 1 - max similarity
    return 1.0 - max_sim

def fitness(r):
    names=[i["ingredient"] for i in r["ingredients"]]
    must_have = [
        any("flour" in tags(n) for n in names),
        any("sweet" in tags(n) for n in names),
        any("fat" in tags(n) for n in names),
        any("binder" in tags(n) or "egg" in tags(n) for n in names),
        any("leavening" in tags(n) for n in names),
        any("salt" in tags(n) for n in names),
    ]
    # if all must have present, score = 6
    score = sum(1 for b in must_have if b)  # 
    # if liquid present, score +1
    score += 1 if any("liquid" in tags(n) for n in names) else 0
    # if inclusion or aroma present, score +1
    score += 1 if any(("inclusion" in tags(n) or "aroma" in tags(n)) for n in names) else 0
    # if 6-10 unique ingredients, score +1
    n=len(names); score += 1 if 6<=n<=10 else 0
    # if ingredients are not too dominant, rasio <=0.6, score +1
    if r["ingredients"]:
        tot = sum(amount_in_grams(i, tags)for i in r["ingredients"]) or 1
        dom = max(amount_in_grams(i, tags)/tot for i in r["ingredients"])
        score += 1 if dom<=0.6 else 0

    score += int(novelty_score(r, recipes) * 10)  # 
    
    return score


"""We can use this to evaluate the initial population."""

evaluate_recipes(population)
population = sorted(population, reverse = True, key = lambda r: r['fitness'])

pprint.PrettyPrinter(indent=2, depth=2).pprint(population)

"""## Selecting Recipes

The following function implements Roulette Wheel selection of individuals based on their fitness:
"""

def select_recipe(recipes):
  sum_fitness = sum([recipe['fitness'] for recipe in recipes])
  f = random.uniform(0, sum_fitness)
  for recipe in recipes:
    if f < recipe['fitness']:
      return recipe
    f -= recipe['fitness']
  return recipes[-1]

"""## Genetic Operators

The following functions implement the genetic operators of crossover and mutation. 
Crossover takes two recipes and combines them by a point on each genotype (recipe) to split each list into two,
and joining the first sublist from one genotype with the second sublist of the second genotype.
"""

recipe_number = 1

def crossover_recipes(r1, r2):
  global recipe_number
#   p1 = random.randint(1, len(r1['ingredients'])-1)
#   p2 = random.randint(1, len(r2['ingredients'])-1)
#   r1a = r1['ingredients'][0:p1]
#   r2b = r2['ingredients'][p2:-1]

  r1a = [x.copy() for x in r1["ingredients"][:max(1,len(r1["ingredients"])//2)]]
  r2b = [x.copy() for x in r2["ingredients"][max(1,len(r2["ingredients"])//2):]]
  r = dict()
  r['name'] = "recipe {}".format(recipe_number)
  recipe_number += 1
  r['ingredients'] = r1a + r2b
  return r

"""The mutation operator changes a recipe using one of four different types of mutations: 
(1) changing the amount of an ingredient, 
(2) changing the type of an ingredient, 
(3) adding an ingredient,  
(4) removing an ingredient,
(5) swapping an ingredient with another of the same class
(6) transferring some amount between two ingredients
"""


def mutate_recipe(r):
    def _same_class_candidates(base_name):
        base_tags = tags(base_name)
        if not base_tags:
            return []
        return [x for x in all_ingredients if tags(x["ingredient"]) & base_tags]
    
    op = random.choice(['amt','swap','add','del', 'class_swap', 'ratio'])
    if r['ingredients'] and op == 'amt':
        # print("mutate amt \n ")
        i = random.choice(r['ingredients'])
        i['amount'] += math.floor(i['amount'] * random.choice([-0.2,0.2]))
        i['amount'] = max(1, i['amount'])
#         r["ingredients"][i]["amount"] = max(1,int(r["ingredients"][i]["amount"] * (1 + random.uniform(-0.2, 0.2)))
# )
    elif r['ingredients'] and op == 'swap':
        # print("mutate swap \n ")
        i = random.choice(r['ingredients'])
        pick = random.choice(all_ingredients).copy()
        pick['amount'] = i['amount']
        pick['unit'] = i.get('unit','g')
        i.update(pick)
    elif op == 'add':
        # print("mutate add \n ")
        r['ingredients'].append(random.choice(all_ingredients).copy())
    elif len(r['ingredients']) > 1 and op == 'del':
        r['ingredients'].remove(random.choice(r['ingredients']))
    
    elif r["ingredients"] and op == 'class_swap':
        # print("mutate class_swap \n")
        i = random.randrange(len(r["ingredients"]))
        base = r["ingredients"][i]
        cands = _same_class_candidates(base["ingredient"])
        if cands:
            repl = copy.deepcopy(random.choice(cands))
            repl["amount"] = base["amount"]
            repl["unit"]   = base.get("unit", "g")
            r["ingredients"][i] = repl
        
    elif len(r["ingredients"]) >= 2 and op == 'ratio':
        # print("mutate ratio \n ")
        # radio transfer between two ingredients
        a, b = random.sample(r["ingredients"], 2)
        if a["amount"] > 1:
            delta = max(1, int(a["amount"] * random.uniform(0.05, 0.25)))
            a["amount"] = max(1, a["amount"] - delta)
            b["amount"] += delta
    # normalise_recipe(r)

"""The following function is domain-specific and normalises a generated recipe by removing duplicate ingredients (combining the amounts of all instances of an ingredient) and rescaling the volume of ingredients listed to 1 litre (1000 units)."""

def normalise_recipe(r):
  unique_ingredients = dict()
  for i in r['ingredients']:
    name = i['ingredient']
    g = amount_in_grams(i, tags)
    if name in unique_ingredients:
      n = unique_ingredients[name]
      n['weight'] += g
    else:
      new_i = i.copy()
      new_i['weight'] = g
      unique_ingredients[name] = new_i

  ingredients = list(unique_ingredients.values())
  total_g = sum(i["weight"] for i in ingredients) or 1.0

#   sum_amounts = sum([i['amount'] for i in r['ingredients']])

  scale = 1000 / total_g
  for i in ingredients:
    
    # i['amount'] = max(1, math.floor(i['amount'] * scale))
    i["weight"] *= scale
    # write back to amount and unit
    i["amount"] = max(1, math.floor(i["weight"]))
    i["unit"] = "g"


  r['ingredients'] = ingredients

"""## Generating Recipes

We use the above functions to generate recipes.
"""

def generate_recipes(size, population):
  R = []
  while len(R) < size:
    r1 = select_recipe(population)
    # print("r1:", r1, "\n")
    r2 = select_recipe(population)
    # print("r2:", r2, "\n")
    r = crossover_recipes(r1, r2)
    # print("crossover:", r, "\n")
    mutate_recipe(r)
    # print("mutate:", r, "\n")
    normalise_recipe(r)
    # print("normalise:", r, "\n")
    R.append(r)
  evaluate_recipes(R)
  return R

"""## Selecting a New Population

The final function that we need to implement is one that selects a new population given the previous population and the generated recipes.
"""

def select_population(P, R):
  R = sorted(R, reverse = True, key = lambda r: r['fitness'])
  P = P[0:len(P)//2] + R[0:len(R)//2]
  P = sorted(P, reverse = True, key = lambda r: r['fitness'])
  return P

"""## Putting it All Together...

To run the genetic algorithm, we repeat here the code to set up and evaluated an initial population, before running the evolutionary process for a number of steps.
"""

population = random.choices(recipes, k=population_size)
evaluate_recipes(population)
population = sorted(population, reverse = True, key = lambda r: r['fitness'])


MAX_GEN = 1000
early_stop_rounds = 1000

best_fitness = 0
no_improve = 0

max_fitnesses = []
min_fitnesses = []
for i in range(MAX_GEN):
  R = generate_recipes(population_size, population)
  population = select_population(population, R)
  max_fitnesses.append(population[0]['fitness'])
  min_fitnesses.append(population[-1]['fitness'])
  
  current_best = population[0]['fitness']
  if current_best > best_fitness:
    best_fitness = current_best
    no_improve = 0
  else:
    no_improve += 1

  if no_improve >= early_stop_rounds:
    print(f"Early stopping at generation {i}")
    break
  

best_recipe = population[0]

with open("data/best_recipe.json", "w", encoding="utf-8") as f:
    json.dump(best_recipe, f, indent=2, ensure_ascii=False)


print("lenth of final population:", len(population))
print("best fitness:", population[0]['fitness'])
print("worst fitness:", population[-1]['fitness'])

with open("data/generated_recipes.json", "w", encoding="utf-8") as f:
    json.dump(population, f, indent=2, ensure_ascii=False)

"""We can check on the progress of the evolution by plotting the fitness history we captured above. Here we plot both the maximum fitness each population and the range fitnesses (filling between max fitness and min fitness)."""

import matplotlib.pyplot as plt

x  = range(len(max_fitnesses))
plt.plot(x, max_fitnesses, label="line L")
plt.fill_between(x, min_fitnesses, max_fitnesses, alpha=0.2)
plt.plot()

plt.xlabel("generation")
plt.ylabel("fitness")
plt.title("fitness over time")
plt.legend()
plt.show()

"""Finally, because the recipe is always sorted according to fitness, the fittest individual will be the one in the first position, so we can print this out."""

# pprint.PrettyPrinter(indent=2, depth=3).pprint(population[0])