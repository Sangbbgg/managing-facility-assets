import client from './client'

export const softwareApi = {
  getAll: (assetId) => client.get(`/api/assets/${assetId}/software`).then((r) => r.data),
  updateAccountStatus: (assetId, disabledAccountIds) =>
    client.patch(`/api/assets/${assetId}/software/accounts/status`, {
      disabled_account_ids: disabledAccountIds,
    }).then((r) => r.data),
  remove: (assetId, type, swId) => client.delete(`/api/assets/${assetId}/software/${type}/${swId}`),
}
