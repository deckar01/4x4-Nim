<template>
  <div class="container">
    <Keypress key-event="keypress" :key-code="13" @success="commit" prevent-default/>
    <Keypress key-event="keypress" :key-code="32" @success="commit" prevent-default/>
    <div class="row" v-for="(row, y) in board" :key="y">
      <div class="cell" v-for="(piece, x) in row" :key="x"
        :class="{piece, ready, valid: valid(x, y), selected: selected(x, y)}"
        @click="select(x, y)"
      >
        <div class="content">{{ rowNames[y] }}{{ columnNames[x] }}</div>
      </div>
    </div>
    <div class="history">
      <span class="content" v-for="(move, index) in history" :key="index">{{ move }} </span>
    </div>
    <div class="status">
      <span class="content">{{ status }}</span>
    </div>
  </div>
</template>

<script>
const rowMap = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
const columnMap = {'1': 0, '2': 1, '3': 2, '4': 3}

export default {
  name: 'Game',
  components: {
    Keypress: () => import('vue-keypress')
  },
  props: {
    history: Array,
    status: String,
  },
  data() {
    return {
      rowNames: 'ABCD',
      columnNames: '1234',
      selection: [],
    }
  },
  computed: {
    ready() {
      return this.status == "Your turn"
    },
    board() {
      const board = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
      this.history.map(this.read).flat().forEach(([x, y]) => board[x][y] = 0)
      return board
    },
    _minX() {
      return this.selection.map(s => s[0]).reduce((p, c) => Math.min(p, c), 4)
    },
    _maxX() {
      return this.selection.map(s => s[0]).reduce((p, c) => Math.max(p, c), -1)
    },
    _minY() {
      return this.selection.map(s => s[1]).reduce((p, c) => Math.min(p, c), 4)
    },
    _maxY() {
      return this.selection.map(s => s[1]).reduce((p, c) => Math.max(p, c), -1)
    },
    minX() {
      const x = this._minX - 1
      const y = this.selection[0][1]
      return x >= 0 && this.board[y][x] ? x : -1
    },
    maxX() {
      const x = this._maxX + 1
      const y = this.selection[0][1]
      return x <= 3 && this.board[y][x] ? x : 4
    },
    minY() {
      const y = this._minY - 1
      const x = this.selection[0][0]
      return y >= 0 && this.board[y][x] ? y : -1
    },
    maxY() {
      const y = this._maxY + 1
      const x = this.selection[0][0]
      return y <= 3 && this.board[y][x] ? y : 4
    },
    move() {
      const [a, b] = this.selection[0]
      if(this.selection.length == 1)
        return this.rowNames[b] + this.columnNames[a]
      const [c, d] = this.selection[1]
      if(a == c)
        return this.rowNames[this._minY] + this.rowNames[this._maxY] + this.columnNames[c]
      return this.rowNames[d] + this.columnNames[this._minX] + this.columnNames[this._maxX]
    }
  },
  methods: {
    read(move) {
      const y = rowMap[move[0]]
      // Single piece
      if(move.length == 2)
        return [[y, columnMap[move[1]]]]
      const z = columnMap[move[2]]
      const pieces = []
      // Horizontal pieces
      if(rowMap[move[1]] !== undefined)
        for(let x = y; x <= rowMap[move[1]]; x += 1)
          pieces.push([x, z])
      // Vertical pieces
      else
        for(let x = columnMap[move[1]]; x <= z; x += 1)
          pieces.push([y, x])
      return pieces
    },
    valid(x, y) {
      if(!this.ready || !this.board[y][x])
        return false
      if(this.selection.length == 0)
        return true
      const [a, b] = this.selection[0]
      if(this.selection.length == 1)
        return (a == x && Math.abs(b - y) == 1) || (b == y && Math.abs(a - x) == 1)
      const [c, d] = this.selection[1]
      if(a == c)
        return x == c && (y == this.minY || y == this.maxY)
      return y == d && (x == this.minX || x == this.maxX)
    },
    select(x, y) {
      const selected = this.selected(x, y)
      const valid = this.valid(x, y)
      if(selected || !valid)
        return this.selection = []
      if(!selected)
        this.selection.push([x, y])
    },
    selected(x, y) {
      for(let [a, b] of this.selection)
        if(a == x && b == y)
          return true
      return false
    },
    commit() {
      if(!this.selection.length && this.history.length)
        return
      if(!this.selection.length && !this.history.length)
        this.$emit('pass')
      if(this.selection.length)
        this.$emit('move', this.move)
      this.selection = []
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.history,
.status {
  margin: 5px;
  padding: 20px;
  background-color: #080808;
  border-radius: 2px;
}

.row {
  display: flex;
  flex-wrap: wrap;
}

.cell {
  border-radius: 5%;
  background-color: #040404;
  border: 1px solid #040404;
  transition: background-color 200ms ease-in-out, border-color 200ms ease-in-out;
  position: relative;
  flex-basis: calc(25% - 10px);
  margin: 5px;
  box-sizing: border-box;
}

.piece {
  background-color: #151515;
  border-color: #404040;
}

.piece.ready {
  cursor: pointer;
}

.piece.ready:hover {
  background-color: #404040;
}

.piece.selected {
  background-color: #C00000;
  border-color: #B0A0A0;
}

.piece.selected:hover {
  background-color: #900000;
}

.piece.valid {
  background-color: #000040;
  border-color: #404080;
}

.piece.valid:hover {
  background-color: #404080;
}

.cell::before {
  content: '';
  display: block;
  padding-top: 100%;
}

.content {
  font-family: monospace;
  color: rgba(255, 255, 255, 0.4);
}

.cell .content {
  pointer-events: none;
  user-select: none;
  position: absolute;
  top: 0; left: 0;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.history {
  margin-top: 20px;
}
</style>
