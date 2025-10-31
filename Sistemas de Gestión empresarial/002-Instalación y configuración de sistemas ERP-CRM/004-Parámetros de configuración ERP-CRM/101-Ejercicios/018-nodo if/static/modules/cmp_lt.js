import { buildSimpleCompareBody, readSimple, renderBool } from "/static/modules/cmp_common.js";
export default {
  type: "cmp_lt",
  buildBody(el){ buildSimpleCompareBody(el, "Constante (<)", "0"); },
  readConfig: readSimple,
  renderResult: renderBool
};
