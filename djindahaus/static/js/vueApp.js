Vue.use(VueLoading);

const url = 'https://hygiea.carthage.edu/apps/mapache/indahaus/clients/all/';
const app = new Vue({
  delimiters: ['[[', ']]'],
  el: '#app',
  components: {
    Loading: VueLoading
  },
  data: {
    results: []
  },
  mounted() {
    let loader = this.$loading.show({
      loader: 'spinner'
    });
    window.setInterval(() => {
      //$.get(url, function (response) {
        //this.results = response.data;
      //}.bind(this));
      axios.get(url).then(response => {
        this.results = response.data
      })
      .then((response) => {
        loader.hide();
      }, (error) => {
        console.log(error);
      });
    }, 10000);
  }
});
