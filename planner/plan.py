import json
import pulp


def generate_plan_ilp(recipes, rules):
    days = rules["days"]
    meals_per_day = rules["meals_per_day"]
    min_cal = rules["calories"]["min_per_day"]
    max_cal = rules["calories"]["max_per_day"]
    max_repeats = rules["max_repeats_per_recipe"]
    no_consecutive = rules["no_consecutive_duplicates"]

    slots = days * meals_per_day
    recipe_ids = [r["id"] for r in recipes]

    # Create problem
    model = pulp.LpProblem("MealPlan", pulp.LpMinimize)

    # Decision variables
    x = pulp.LpVariable.dicts(
        "assign",
        (recipe_ids, range(slots)),
        cat="Binary"
    )

    # Dummy objective
    model += 0

    # 1️⃣ One recipe per slot
    for s in range(slots):
        model += pulp.lpSum(x[r][s] for r in recipe_ids) == 1

    # 2️⃣ Max repeats
    for r in recipe_ids:
        model += pulp.lpSum(x[r][s] for s in range(slots)) <= max_repeats

    # 3️⃣ Daily calorie bounds
    for d in range(days):
        day_slots = range(d * meals_per_day, (d + 1) * meals_per_day)
        total_calories = pulp.lpSum(
            recipes[i]["calories"] * x[recipes[i]["id"]][s]
            for i in range(len(recipes))
            for s in day_slots
        )
        model += total_calories >= min_cal
        model += total_calories <= max_cal

    # 4️⃣ No consecutive duplicates
    if no_consecutive:
        for r in recipe_ids:
            for s in range(slots - 1):
                model += x[r][s] + x[r][s + 1] <= 1

    # Solve
    model.solve()

    if pulp.LpStatus[model.status] != "Optimal":
        raise ValueError("No feasible meal plan found")

    # Extract plan
    plan = []
    for s in range(slots):
        for r in recipe_ids:
            if pulp.value(x[r][s]) == 1:
                plan.append(r)

    return plan

if __name__ == "__main__":
    recfile = open("recipes.json", "r")
    rulfile = open("rules.json", "r")

    recipes = json.load(recfile)
    rules = json.load(rulfile)
    plan = generate_plan_ilp(recipes, rules)
    print(plan)
