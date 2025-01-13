let fs = require("fs"),
  deasync = require("deasync"),

  // Each 2x2 square is one cell
  load_source = r => fs.readFileSync(r, "utf-8").split("\n").reduce(
    (acc, line, y, lines) => (
      y % 2 == 0 && acc.push(
        Array.from(
          {length: Math.ceil(line.length / 2)},
          (val, x) => lines[y][2 * x] + lines[y][2 * x + 1] + lines[y + 1][2 * x] + lines[y + 1][2 * x + 1]
        )
      ), acc
    ),
    []
  ),

  is_halt = (program_grid, x, y) => y < 0 || y >= program_grid.length || x < 0 || x >= program_grid[0].length,
  bounds_check = (program_grid, x, y) => {
    if (is_halt(program_grid, x, y))
      throw Error("Out of bounds.")
  },

  n = e => r => (e(r), r),
  dx = 1,
  dy = 0,
  x = 0,
  y = 0,
  history = [],

  main_loop = program_grid => {
    for (;!is_halt(program_grid, x, y); x += dx, y += dy)
      program_step(program_grid),
      history.push([dx, dy, x, y, program_grid])
  },
  c = e => {
    [dx, dy, x, y, t] = history[history.length - e],
    history = history.slice(0, -e),
    i(t)
  },
  cell_value = cell_contents => [...cell_contents].reduce((acc, character, index) => 94 * acc + (cell_contents.charCodeAt(index) - 32), 0),
  value_to_ninety_four_string = restult => Array.from({length: 4}).reduce((acc, o, _) => String.fromCharCode(32 + Math.floor(restult / 94 ** _) % 94) + acc, ""),
  a = (o) => (..._) => value_to_ninety_four_string(o(..._.map(cell_value))),
  to_balanced_twenty_four = cell_tail => [cell_tail % 24 - 11, Math.floor(cell_tail / 24)],
  C = () => {
    let e = null;
    for (process.stdin.once("data", r => e = r); null === e;)
      deasync.runLoopOnce();
    return e.toString().trim()
  },
  get_offset_coords = (program_grid, cell_tail) => {
    let o, _;
    return [offset_y, cell_tail] = to_balanced_twenty_four(cell_tail),
      [offset_x, cell_tail] = to_balanced_twenty_four(cell_tail),
      bounds_check(program_grid, offset_x + x, offset_y + y),
      [offset_x + x, offset_y + y, cell_tail]
  },
  program_step = program_grid => {
    let current_cell_value = cell_value(program_grid[y][x]),
      current_cell_tail = Math.floor(current_cell_value / 94),
      _,
      l = binop => () => {
        let [x1, y1, n] = get_offset_coords(program_grid, current_cell_tail),
          [x2, y2, x] = get_offset_coords(program_grid, n);
        program_grid[y2][x2] = a(binop)(program_grid[y2][x2], program_grid[y1][x1])
      },
      h = unop => () => {
        let [_, l, n] = get_offset_coords(program_grid, current_cell_tail);
        program_grid[l][_] = a(unop)(program_grid[l][_])
      };
    ({1: l((e, r) => e + r),
      2: l((e, r) => e - r),
      3: l((e, r) => e * r),
      4: l((e, r) => e / r),
      5: l((e, r) => e % r),
      6: l((e, r) => e == r),
      7: l((e, r) => e != r),
      8: l((e, r) => e < r),
      9: l((e, r) => e > r),
      10: l((e, r) => e || r),
      11: l((e, r) => e && r),
      12: h(n(e => process.stdout.write(String.fromCharCode(e)))),
      13: h(e => C().charCodeAt(0)),
      14(){dx = 1, dy = 0},
      15(){dx = -1, dy = 0},
      16(){dx = 0, dy = 1},
      17(){dx = 0, dy = -1},
      18: h(n(e => c(e))),
      19: () => process.exit(0),     // halt
      20: h(n(e => process.stdout.write(e.toString()))),
      21: h(e => 0 | C())
    })[current_cell_value % 94]?.()
  };
main_loop(load_source(process.argv[2]))
