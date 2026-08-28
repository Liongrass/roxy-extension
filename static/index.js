window.PageRoxy = {
  template: '#page-roxy',
  computed: {
    baseUrl() {
      return window.location.origin + '/roxy/api/v1/roxies'
    }
  },
  data() {
    return {
      activeUrl: '',
      roxies: [],
      encodingOptions: [
        {label: 'Raw URL', value: 'url'},
        {label: 'LNURL', value: 'lnurl'}
      ],
      roxyTable: {
        columns: [
          {
            name: 'title',
            label: 'Title',
            align: 'left',
            field: 'title'
          },
          {
            name: 'target_url',
            label: 'Target',
            align: 'left',
            field: 'target_url'
          },
          {
            name: 'encoding',
            label: 'Shared as',
            align: 'left',
            format: (_, row) => (row.encoding === 'lnurl' ? 'LNURL' : 'URL')
          },
          {
            name: 'status',
            label: 'Status',
            align: 'left',
            format: (_, row) => (row.is_enabled ? '🟢 Enabled' : '⚫ Disabled')
          },
          {
            name: 'created_at',
            label: 'Created',
            align: 'left',
            field: 'created_at',
            format: val => (val ? LNbits.utils.formatDate(val) : '—')
          }
        ],
        pagination: {rowsPerPage: 10}
      },
      formDialog: {
        show: false,
        data: {
          encoding: 'url'
        }
      },
      editDialog: {
        show: false,
        data: null
      },
      qrCodeDialog: {
        show: false,
        data: null
      }
    }
  },
  methods: {
    activeUrlFor(roxy) {
      // Always the raw URL: lnbits-qrcode-lnurl bech32-encodes it itself for
      // display/QR/copy, so feeding it roxy.lnurl here would double-encode it.
      return roxy.proxy_url
    },
    getRoxies() {
      LNbits.api
        .request(
          'GET',
          '/roxy/api/v1/roxies?all_wallets=true',
          this.g.user.wallets[0].inkey
        )
        .then(response => {
          this.roxies = response.data
        })
        .catch(LNbits.utils.notifyApiError)
    },
    openQrCodeDialog(roxyId) {
      const roxy = this.roxies.find(r => r.id === roxyId)
      if (!roxy) return
      this.activeUrl = this.activeUrlFor(roxy)
      this.qrCodeDialog.data = roxy
      this.qrCodeDialog.show = true
    },
    openEditDialog(roxyId) {
      const roxy = this.roxies.find(r => r.id === roxyId)
      if (!roxy) return
      this.editDialog.data = {
        id: roxy.id,
        wallet: roxy.wallet,
        title: roxy.title,
        target_url: roxy.target_url,
        encoding: roxy.encoding,
        is_enabled: roxy.is_enabled
      }
      this.editDialog.show = true
    },
    createRoxy() {
      const wallet = this.g.user.wallets.find(
        w => w.id === this.formDialog.data.wallet
      )
      if (!wallet) return

      LNbits.api
        .request('POST', '/roxy/api/v1/roxies', wallet.adminkey, {
          title: this.formDialog.data.title,
          wallet: wallet.id,
          target_url: this.formDialog.data.target_url,
          encoding: this.formDialog.data.encoding
        })
        .then(response => {
          this.roxies.unshift(response.data)
          this.formDialog.show = false
          this.resetFormData()
        })
        .catch(LNbits.utils.notifyApiError)
    },
    saveRoxy() {
      const data = this.editDialog.data
      const wallet = this.g.user.wallets.find(w => w.id === data.wallet)
      if (!wallet) return

      LNbits.api
        .request('PUT', `/roxy/api/v1/roxies/${data.id}`, wallet.adminkey, {
          title: data.title,
          target_url: data.target_url,
          encoding: data.encoding,
          is_enabled: data.is_enabled
        })
        .then(response => {
          const index = this.roxies.findIndex(r => r.id === data.id)
          if (index !== -1) this.roxies.splice(index, 1, response.data)
          this.editDialog.show = false
          this.resetEditData()
        })
        .catch(LNbits.utils.notifyApiError)
    },
    deleteRoxy(roxyId) {
      const roxy = this.roxies.find(r => r.id === roxyId)
      if (!roxy) return

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this roxy?')
        .onOk(() => {
          const wallet = this.g.user.wallets.find(w => w.id === roxy.wallet)
          if (!wallet) return

          LNbits.api
            .request(
              'DELETE',
              `/roxy/api/v1/roxies/${roxyId}`,
              wallet.adminkey
            )
            .then(() => {
              this.roxies = this.roxies.filter(r => r.id !== roxyId)
            })
            .catch(LNbits.utils.notifyApiError)
        })
    },
    resetFormData() {
      this.formDialog = {
        show: false,
        data: {
          encoding: 'url'
        }
      }
    },
    resetEditData() {
      this.editDialog = {
        show: false,
        data: null
      }
    }
  },
  created() {
    if (this.g.user.wallets?.length) {
      this.getRoxies()
    }
  }
}
