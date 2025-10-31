import { buildSimpleCompareBody, readSimple, renderBool } from "/static/modules/cmp_common.js";
export default {
  type: "cmp_eq",
  buildBody(el){ buildSimpleCompareBody(el, "Constante (==)", ""); },
  readConfig: readSimple,
  renderResult: renderBool
};
