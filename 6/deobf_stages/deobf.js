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

  n = e => r => (e(r), r), // !!! SIDE EFFECTS !!!
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
    main_loop(t)
  },
  cell_value = cell_contents => [...cell_contents].reduce(
    (acc, _, index) => 94 * acc + (cell_contents.charCodeAt(index) - 32),
    0
  ),
  value_to_ninety_four_string = restult => Array.from({length: 4}).reduce(
    (acc, _, index) => String.fromCharCode(32 + Math.floor(restult / 94 ** index) % 94) + acc,
    ""
  ),
  apply = (op) => (..._) => value_to_ninety_four_string(op(..._.map(cell_value))),
  to_balanced_twenty_four = cell_tail => [cell_tail % 24 - 11, Math.floor(cell_tail / 24)],
  C = () => {
    let e = null;
    for (process.stdin.once("data", r => e = r); null === e;)
      deasync.runLoopOnce();
    console.log(e)
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
    console.log(program_grid);
    let current_cell_value = cell_value(program_grid[y][x]),
      current_cell_tail = Math.floor(current_cell_value / 94),
      l = binop => () => {
        let [x1, y1, n] = get_offset_coords(program_grid, current_cell_tail),
          [x2, y2, _] = get_offset_coords(program_grid, n);
        program_grid[y2][x2] = apply(binop)(program_grid[y2][x2], program_grid[y1][x1])
      },
      h = unop => () => {
        let [x1, y1, n] = get_offset_coords(program_grid, current_cell_tail);
        program_grid[y1][x1] = apply(unop)(program_grid[y1][x1])
      };
    console.log("At x:", x, " y:", y);
    console.log("Doing command:", current_cell_value % 94);
    if (current_cell_tail > 0) {
      let [x1, y1, n] = get_offset_coords(program_grid, current_cell_tail);
      console.log("First argument:", y1, x1);
      if (n > 0) {
        let [x2, y2, _] = get_offset_coords(program_grid, n);
        console.log("Second argument:", y2, x2);
      }
    }
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
      // print from char code
      12: h(n(e => process.stdout.write(String.fromCharCode(e)))),
      13: h(e => C().charCodeAt(0)),  // read first character's ASCII value?
      14(){dx = 1, dy = 0},           // > turn right (let's sit down)
      15(){dx = -1, dy = 0},          // < turn left
      16(){dx = 0, dy = 1},           // v turn down (for what?)
      17(){dx = 0, dy = -1},          // ^ turn up
      // Going back in time doesn't change the grid, only gets the previous
      // coordinates and direction (I think). It *tries* to change the grid but
      // since it's stored by reference it doesn't work. It will run the program
      // from those coords until it goes out of bounds, and then overwrite the
      // cell with the value it had when it got called. This returning behavior
      // is barely useful.
      18: h(n(e => c(e))),            // go back in time
      19: () => process.exit(0),      // halt
      // print a number
      20: h(n(e => process.stdout.write(e.toString()))),
      21: h(e => 0 | C())             // read a number from input
    })[current_cell_value % 94]?.()
  };
main_loop(load_source(process.argv[2]))
