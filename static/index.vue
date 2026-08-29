<template id="page-roxy">
  <div class="row q-col-gutter-md">
    <!-- ── Left column: table + create button ── -->
    <div class="col-12 col-md-7 q-gutter-y-md">
      <q-card>
        <q-card-section>
          <q-btn unelevated color="primary" @click="formDialog.show = true">
            New Roxy
          </q-btn>
        </q-card-section>
      </q-card>

      <q-card>
        <q-card-section>
          <div class="row items-center no-wrap q-mb-md">
            <div class="col">
              <h5 class="text-subtitle1 q-my-none">Roxies</h5>
            </div>
          </div>
          <q-table
            dense
            flat
            :rows="roxies"
            :columns="roxyTable.columns"
            row-key="id"
            v-model:pagination="roxyTable.pagination"
          >
            <template v-slot:header="props">
              <q-tr class="text-left" :props="props">
                <q-th auto-width></q-th>
                <q-th v-for="col in props.cols" :key="col.name" :props="props">
                  <span v-text="col.label"></span>
                </q-th>
              </q-tr>
            </template>
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td auto-width>
                  <q-btn
                    dense
                    size="xs"
                    icon="visibility"
                    :color="$q.dark.isActive ? 'grey-7' : 'grey-5'"
                    class="q-ml-sm"
                    @click="openQrCodeDialog(props.row.id)"
                  >
                    <q-tooltip>View QR / URL</q-tooltip>
                  </q-btn>
                  <q-btn
                    dense
                    size="xs"
                    icon="edit"
                    :color="$q.dark.isActive ? 'grey-7' : 'grey-5'"
                    class="q-ml-sm"
                    @click="openEditDialog(props.row.id)"
                  >
                    <q-tooltip>Edit target</q-tooltip>
                  </q-btn>
                  <q-btn
                    flat
                    dense
                    size="xs"
                    icon="cancel"
                    color="pink"
                    class="q-ml-sm"
                    @click="deleteRoxy(props.row.id)"
                  >
                    <q-tooltip>Delete</q-tooltip>
                  </q-btn>
                </q-td>
                <q-td
                  v-for="col in props.cols"
                  :key="col.name"
                  :props="props"
                  v-text="col.value"
                ></q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>

    <!-- ── Right column: about + API docs ── -->
    <div class="col-12 col-md-5 q-gutter-y-md">
      <q-card>
        <q-card-section>
          <h6 class="text-subtitle1 q-my-none">Roxy extension</h6>
        </q-card-section>
        <q-card-section class="q-pa-none">
          <q-separator></q-separator>
          <q-list>
            <q-expansion-item
              group="extras"
              icon="swap_vertical_circle"
              label="API info"
              :content-inset-level="0.5"
            >
              <q-btn flat label="Swagger API" type="a" href="../docs#/roxy"></q-btn>
              <q-expansion-item
                group="api"
                dense
                expand-separator
                label="List roxies"
              >
                <q-card>
                  <q-card-section>
                    <code
                      ><span class="text-blue">GET</span>
                      /roxy/api/v1/roxies</code
                    >
                    <h5 class="text-caption q-mt-sm q-mb-none">Headers</h5>
                    <code>{"X-Api-Key": &lt;invoice_key&gt;}</code>
                    <h5 class="text-caption q-mt-sm q-mb-none">Returns 200 OK</h5>
                    <code>[&lt;roxy_object&gt;, ...]</code>
                    <h5 class="text-caption q-mt-sm q-mb-none">Curl example</h5>
                    <code
                      >curl -X GET
                      <span v-text="baseUrl"></span>
                      -H "X-Api-Key:
                      <span v-text="g.user.wallets[0].inkey"></span>"
                    </code>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
              <q-expansion-item
                group="api"
                dense
                expand-separator
                label="Create a roxy"
              >
                <q-card>
                  <q-card-section>
                    <code
                      ><span class="text-green">POST</span>
                      /roxy/api/v1/roxies</code
                    >
                    <h5 class="text-caption q-mt-sm q-mb-none">Headers</h5>
                    <code>{"X-Api-Key": &lt;admin_key&gt;}</code>
                    <h5 class="text-caption q-mt-sm q-mb-none">
                      Body (application/json)
                    </h5>
                    <code
                      >{"title": &lt;string&gt;, "target_url": &lt;string&gt;,
                      "encoding": "url"|"lnurl", "is_enabled":
                      &lt;boolean, default true&gt;}</code
                    >
                    <h5 class="text-caption q-mt-sm q-mb-none">
                      Returns 201 CREATED
                    </h5>
                    <code>{"id": ..., "proxy_url": ..., "lnurl": ..., ...}</code>
                    <h5 class="text-caption q-mt-sm q-mb-none">Curl example</h5>
                    <code
                      >curl -X POST
                      <span v-text="baseUrl"></span>
                      -d
                      '{"title":"My link","target_url":"https://example.com","encoding":"url"}'
                      -H "Content-type: application/json"
                      -H "X-Api-Key:
                      <span v-text="g.user.wallets[0].adminkey"></span>"
                    </code>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
              <q-expansion-item
                group="api"
                dense
                expand-separator
                label="Update a roxy"
              >
                <q-card>
                  <q-card-section>
                    <code
                      ><span class="text-orange">PUT</span>
                      /roxy/api/v1/roxies/&lt;roxy_id&gt;</code
                    >
                    <h5 class="text-caption q-mt-sm q-mb-none">Headers</h5>
                    <code>{"X-Api-Key": &lt;admin_key&gt;}</code>
                    <h5 class="text-caption q-mt-sm q-mb-none">
                      Body (application/json, all fields optional)
                    </h5>
                    <code
                      >{"title": &lt;string&gt;, "target_url": &lt;string&gt;,
                      "encoding": "url"|"lnurl", "is_enabled":
                      &lt;boolean&gt;}</code
                    >
                    <h5 class="text-caption q-mt-sm q-mb-none">
                      Returns 200 OK
                    </h5>
                    <h5 class="text-caption q-mt-sm q-mb-none">Curl example</h5>
                    <code
                      >curl -X PUT
                      <span v-text="baseUrl + '/&lt;roxy_id&gt;'"></span>
                      -d '{"target_url":"https://example.org"}'
                      -H "Content-type: application/json"
                      -H "X-Api-Key:
                      <span v-text="g.user.wallets[0].adminkey"></span>"
                    </code>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
              <q-expansion-item
                group="api"
                dense
                expand-separator
                label="Delete a roxy"
                class="q-pb-md"
              >
                <q-card>
                  <q-card-section>
                    <code
                      ><span class="text-pink">DELETE</span>
                      /roxy/api/v1/roxies/&lt;roxy_id&gt;</code
                    >
                    <h5 class="text-caption q-mt-sm q-mb-none">Headers</h5>
                    <code>{"X-Api-Key": &lt;admin_key&gt;}</code>
                    <h5 class="text-caption q-mt-sm q-mb-none">
                      Returns 200 OK
                    </h5>
                    <h5 class="text-caption q-mt-sm q-mb-none">Curl example</h5>
                    <code
                      >curl -X DELETE
                      <span v-text="baseUrl + '/&lt;roxy_id&gt;'"></span>
                      -H "X-Api-Key:
                      <span v-text="g.user.wallets[0].adminkey"></span>"
                    </code>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
            </q-expansion-item>
            <q-separator></q-separator>
            <q-expansion-item group="extras" icon="info" label="About Roxy">
              <q-card>
                <q-card-section>
                  <p>
                    <strong>Roxy</strong> is a generic HTTP redirector. Create
                    a roxy pointing at any URL (or LNURL) as its
                    <em>target</em>. Roxy hands you back a stable public link
                    &mdash; shown as a raw URL or as a bech32 LNURL, your
                    choice &mdash; along with a QR code.
                  </p>
                  <p>
                    Share that link/QR once. Visitors are redirected to
                    whatever the target currently is. Change the target any
                    time, through this UI or the API, and every copy of the
                    QR code you already handed out keeps working &mdash; now
                    redirecting wherever you last set it.
                  </p>
                  <p>
                    If a target is itself an LNURL, Roxy decodes it to the
                    URL it points to before redirecting, so an existing
                    LNURL-pay/withdraw endpoint can be re-hosted behind a
                    link you control. Roxy never fetches the target itself
                    &mdash; your own wallet or browser follows the redirect.
                  </p>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </q-list>
        </q-card-section>
      </q-card>
    </div>

    <!-- ── Create dialog ── -->
    <q-dialog v-model="formDialog.show" @hide="resetFormData">
      <q-card class="q-pa-lg q-pt-xl lnbits__dialog-card">
        <q-form @submit="createRoxy" class="q-gutter-md">
          <q-select
            filled
            dense
            emit-value
            v-model="formDialog.data.wallet"
            :options="g.user.walletOptions"
            label="Wallet *"
          ></q-select>
          <q-input
            filled
            dense
            v-model.trim="formDialog.data.title"
            type="text"
            label="Title / description *"
          ></q-input>
          <q-input
            filled
            dense
            v-model.trim="formDialog.data.target_url"
            type="text"
            label="Target URL or LNURL *"
            hint="Where visitors to this roxy's link get redirected"
          ></q-input>
          <q-select
            filled
            dense
            emit-value
            map-options
            v-model="formDialog.data.encoding"
            :options="encodingOptions"
            label="Share as"
          ></q-select>
          <div class="row q-mt-lg">
            <q-btn
              unelevated
              color="primary"
              type="submit"
              :disable="
                !formDialog.data.wallet ||
                !formDialog.data.title ||
                !formDialog.data.target_url
              "
            >
              Create Roxy
            </q-btn>
            <q-btn v-close-popup flat color="grey" class="q-ml-auto">
              Cancel
            </q-btn>
          </div>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- ── Edit dialog ── -->
    <q-dialog v-model="editDialog.show" @hide="resetEditData">
      <q-card class="q-pa-lg q-pt-xl lnbits__dialog-card">
        <q-form @submit="saveRoxy" class="q-gutter-md">
          <q-input
            filled
            dense
            v-model.trim="editDialog.data.title"
            type="text"
            label="Title / description *"
          ></q-input>
          <q-input
            filled
            dense
            v-model.trim="editDialog.data.target_url"
            type="text"
            label="Target URL or LNURL *"
            hint="Where visitors to this roxy's link get redirected"
          ></q-input>
          <q-select
            filled
            dense
            emit-value
            map-options
            v-model="editDialog.data.encoding"
            :options="encodingOptions"
            label="Share as"
          ></q-select>
          <q-toggle
            v-model="editDialog.data.is_enabled"
            label="Enabled"
          ></q-toggle>
          <div class="row q-mt-lg">
            <q-btn
              unelevated
              color="primary"
              type="submit"
              :disable="!editDialog.data.title || !editDialog.data.target_url"
            >
              Save changes
            </q-btn>
            <q-btn v-close-popup flat color="grey" class="q-ml-auto">
              Cancel
            </q-btn>
          </div>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- ── QR code dialog ── -->
    <q-dialog v-model="qrCodeDialog.show" position="top">
      <q-card v-if="qrCodeDialog.data" class="q-pa-lg lnbits__dialog-card">
        <lnbits-qrcode-lnurl
          v-if="qrCodeDialog.data.encoding === 'lnurl'"
          :url="activeUrl"
          :nfc="true"
        ></lnbits-qrcode-lnurl>
        <lnbits-qrcode v-else :value="activeUrl"></lnbits-qrcode>
        <p style="word-break: break-all" class="q-mt-md">
          <strong>ID:</strong>
          <span v-text="qrCodeDialog.data.id"></span><br />
          <strong>Title:</strong>
          <span v-text="qrCodeDialog.data.title"></span><br />
          <strong>Status:</strong>
          <span v-text="qrCodeDialog.data.is_enabled ? '🟢 Enabled' : '⚫ Disabled'"></span><br />
          <strong>Target:</strong>
          <span v-text="qrCodeDialog.data.target_url"></span>
        </p>
        <div class="row q-mt-lg q-gutter-sm">
          <q-btn
            outline
            color="grey"
            @click="utils.copyText(activeUrl, 'URL copied to clipboard!')"
          >
            Copy URL
          </q-btn>
          <q-btn v-close-popup flat color="grey" class="q-ml-auto">
            Close
          </q-btn>
        </div>
      </q-card>
    </q-dialog>
  </div>
</template>
