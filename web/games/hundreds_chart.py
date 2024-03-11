import random
from datetime import datetime

import jinja2
import tornado

from utils.custom_print import CustomPrint
from utils.sessions import sessions
from utils import globals

loader = jinja2.FileSystemLoader("templates")
env = jinja2.Environment(loader=loader)


class Cell:
    def __init__(self, x: int, y: int, show: bool = False, value=None):
        self.x = x
        self.y = y
        self.show: bool = show
        self.value = value


class Table:
    def __init__(self, size_x: int = 10, size_y: int = 10):
        self.size = (size_x, size_y)
        self.cells: list[list[Cell]] = []
        self.generate()

    def cell_at(self, x, y) -> Cell:
        return self.cells[x][y]

    def is_row_active(self, row) -> bool:
        for x in range(self.size[0]):
            if self.cell_at(row, x).show is True:
                return True
        return False

    def is_col_active(self, col) -> bool:
        for y in range(self.size[1]):
            if self.cell_at(y, col).show is True:
                return True
        return False

    def get_all_cells(self) -> list[Cell]:
        cells: list[Cell] = []
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                cells.append(self.cell_at(x, y))
        return cells

    def generate(self):
        for x in range(self.size[0]):
            self.cells.append([])
            for y in range(self.size[1]):
                cell = Cell(x, y)
                self.cells[x].append(cell)

    def reset_visibility(self):
        for row in self.cells:
            for cell in row:
                cell.show = False

    def find_cell_by_value(self, value) -> Cell:
        for row in self.cells:
            for cell in row:
                if cell.value == value:
                    return cell
        return None

    def walk_to_number(self, start_value: int, end_value: int, randomness_factor: float) -> list[Cell]:
        self.reset_visibility()
        start_cell = self.find_cell_by_value(start_value)
        end_cell = self.find_cell_by_value(end_value)

        if not start_cell or not end_cell:
            return []  # Start or end value not found

        path = [start_cell]
        current_cell = start_cell
        current_cell.show = True  # Mark the starting cell as visible

        while current_cell.value != end_value:
            next_steps = []

            # Add direct steps towards the target
            if current_cell.x < end_cell.x:
                next_steps.append((1, 0))  # Right
            elif current_cell.x > end_cell.x:
                next_steps.append((-1, 0))  # Left
            if current_cell.y < end_cell.y:
                next_steps.append((0, 1))  # Down
            elif current_cell.y > end_cell.y:
                next_steps.append((0, -1))  # Up

            # Add random steps based on the randomness factor
            if random.random() < randomness_factor:
                next_steps.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])  # All directions

            # Choose the next step and ensure it's within bounds
            dx, dy = random.choice(next_steps)
            next_x = max(0, min(current_cell.x + dx, self.size[0] - 1))
            next_y = max(0, min(current_cell.y + dy, self.size[1] - 1))

            current_cell = self.cell_at(next_x, next_y)
            current_cell.show = True  # Mark the cell as part of the path
            path.append(current_cell)

        return path


class HundredsChartHandler(tornado.web.RequestHandler):
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
            charts=self.generate_charts(10),
        )
        self.write(rendered_template)

    def generate_table(self, index: int, starting_number: int, ending_number: int, randomness: float) -> str:
        html = f'<div class="chart" id="chart{index}"><table>'
        table = Table()
        for count, cell in enumerate(table.get_all_cells()):
            cell.value = count + 1
        table.walk_to_number(starting_number, ending_number, randomness)
        for x in range(table.size[0]):
            if not table.is_row_active(x):
                continue
            html += '<tr>'
            for y in range(table.size[1]):
                if not table.is_col_active(y):
                    continue
                number = table.cell_at(x, y).value
                if table.cell_at(x, y).show:
                    if number == starting_number:
                        html += f'<td id="starting_number"><input type="number" answer="{starting_number}" class="chart_number" name="starting_number" value="{starting_number}"></td>'
                    elif number == ending_number:
                        html += f'<td id="ending_number"><input type="number" answer="{ending_number}" class="chart_number" name="ending_number" onChange="checkInputs()"></td>'
                    else:
                        html += '<td class="cell-input"><input type="number" name="input"></td>'
                else:
                    html += '<td></td>'
            html += '</tr>'
        html += f'</table><button class="waves-effect waves-light btn" id="check" onclick="checkChart(\'{index}\')">Check</button></div>'
        return html

    def generate_charts(self, count: int) -> str:
        number_range = globals.games_config["hundreds_chart"][self.grade_level]["number_range"]
        randomness = globals.games_config["hundreds_chart"][self.grade_level]["randomness"]
        charts_html = ""
        for i in range(count):
            starting_number = random.randint(number_range[0], number_range[1] - 10)
            ending_number = max(starting_number + 10, random.randint(number_range[0], number_range[1]))
            charts_html += f'<div class="page" id=page{i+1}>{self.generate_table(i+1, starting_number, ending_number, randomness)}</div>'
        return charts_html
