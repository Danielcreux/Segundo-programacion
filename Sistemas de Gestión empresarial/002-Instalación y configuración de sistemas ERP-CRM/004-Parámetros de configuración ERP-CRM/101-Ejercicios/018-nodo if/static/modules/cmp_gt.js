import { buildSimpleCompareBody, readSimple, renderBool } from "/static/modules/cmp_common.js";
export default {
  type: "cmp_gt",
  buildBody(el){ buildSimpleCompareBody(el, "Constante (>)", "0"); },
  readConfig: readSimple,
  renderResult: renderBool
};
