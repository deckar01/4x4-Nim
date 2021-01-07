<template>
  <div>
    <Game :history="history" :status="status" @move="move" @pass="pass"/>
  </div>
</template>

<script>
import axios from 'axios'
import Game from './components/Game.vue'

export default {
  name: 'App',
  components: {
    Game
  },
  data() {
    return {
      history: this.board(),
      status: "Your turn",
    }
  },
  methods: {
    board() {
      if(window.location.hash.length <= 1)
        return []
      return window.location.hash.slice(1).split(',')
    },
    async move(move) {
      this.history.push(move)
      await this.pass()
    },
    async pass() {
      this.status = "Thinking..."
      const reply = await this.bot()
      this.status = reply.status
      if(reply.move) this.history.push(reply.move)
      window.location.hash = this.history.join(',')
    },
    async bot() {
      const response = await axios.post('http://localhost:5000/', this.history)
      return response.data
    }
  }
}
</script>

<style>
body {
  background-color: #000000;
}
</style>
