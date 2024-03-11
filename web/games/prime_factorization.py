import math
import random
from datetime import datetime
from itertools import combinations_with_replacement

import jinja2
import tornado

from utils.custom_print import CustomPrint
from utils.sessions import sessions
from utils import globals

loader = jinja2.FileSystemLoader("templates")
env = jinja2.Environment(loader=loader)


class PrimeFactorizationHandler(tornado.web.RequestHandler):
    def post(self):
        current_ip = self.request.remote_ip
        if current_ip not in sessions or not sessions[current_ip]["logged_in"]:
            self.redirect("/login")
            return
        self.grade_level = globals.school.get_student_from_name(sessions[current_ip]['username']).get_grade_level()
        game_name = self.get_argument("game")
        entered_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_name = game_name.lower().replace(" ", "_")
        template = env.get_template(f"{html_name}.html")
        sessions[current_ip]["current_game"] = game_name
        sessions[current_ip]["date"] = entered_date
        CustomPrint.print(
            f"INFO - {sessions[current_ip]['username']} entered {game_name}"
        )

        rendered_template = template.render(
            username=sessions[current_ip]["username"],
            game_name=game_name,
            trees=self.generate_trees(10),
        )
        self.write(rendered_template)

    def find_factors(self, n) -> set[int]:
        factors = set()
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                factors.add(i)
                factors.add(n // i)
        return factors

    def product(self, numbers: list[int]) -> int:
        product = 1
        for number in numbers:
            product *= number
        return product

    def generate_combinations(self, factors, n, up_to) -> set[int]:
        result = set()
        for r in range(2, up_to + 1):
            for combo in combinations_with_replacement(factors, r):
                if self.product(combo) == n:
                    result.add(tuple(sorted(combo)))
        return result

    def all_factor_combinations(self, n, up_to) -> list[int]:
        factors = self.find_factors(n)
        combinations = self.generate_combinations(factors, n, up_to)
        return list(combinations)

    def generate_factorization_tree_html(self, index, number, up_to) -> str:
        def factorize(n) -> list[int]:
            factors = self.all_factor_combinations(n, up_to)
            if len(factors) > 0:
                return list(random.choice(factors))
            return [n]

        def build_html_tree(factors, parent=True):
            if len(factors) == 1:
                return f'<li><div><input style="width: 50px; text-align: center;" type="number" answer="{factors[0]}" class="factor" onChange="checkInputs()"></div></li>'
            else:
                sub_tree_html = ""
                for factor in factors:
                    if isinstance(factor, list):
                        sub_tree_html += build_html_tree(factor, False)
                    else:
                        sub_factor = factorize(factor)
                        if len(sub_factor) > 1:
                            sub_tree_html += build_html_tree(sub_factor, False)
                        else:
                            sub_tree_html += f'<li><div><input style="width: 50px; text-align: center;" type="number" answer="{factor}" class="factor" onChange="checkInputs()"></div></li>'
                if parent:
                    return f'<div class="tree" id="tree{index}"><ul><li><div><p style="width: 50px; text-align: center;" id="parentNumber">{number}</p></div><ul>{sub_tree_html}</ul></li></ul></div>'
                else:
                    return f'<li><div><input style="width: 50px; text-align: center;" type="number" answer="{self.product(factors)}" class="factor" onChange="checkInputs()"></div><ul>{sub_tree_html}</ul></li>'

        factors = factorize(number)
        return (
            build_html_tree(factors)
            + f'<button class="waves-effect waves-light btn" id="check" onclick="checkLeafProduct(\'{index}\')">Check</button>'
        )

    def is_prime(self, n):
        if n <= 1:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    def generate_numbers(self, count: int, number_range: list[int]) -> list[int]:
        numbers: set[int] = set()
        while len(numbers) < count:
            new_number = random.randint(number_range[0], number_range[1])
            if self.is_prime(new_number):
                continue
            numbers.add(new_number)
        return list(numbers)

    def generate_trees(self, count):
        number_range = globals.games_config["prime_factorization"][self.grade_level]["number_range"]
        number_of_factors = globals.games_config["prime_factorization"][self.grade_level]["number_of_factors"]
        html_string = ""
        for i, number in enumerate(self.generate_numbers(count, number_range)):
            html_string += f'<div class="page" id=page{i+1}>{self.generate_factorization_tree_html(i+1, number, up_to=number_of_factors)}</div>'
        return html_string
