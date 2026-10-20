// Code node "Build the log row" (all items).
// ---8<---
let pickd = {}; try { pickd = $('Pick new meetings').first().json; } catch (e) {}
let rows = []; try { rows = $('Build the Notion rows').all().map(function (i) { return i.json; }); } catch (e) {}
let made = []; try { made = $('Save the row').all().map(function (i) { return i.json; }); } catch (e) {}
let drafts = []; try { drafts = $('Draft the email').all().map(function (i) { return i.json; }).filter(function (d) { return d && d.id; }); } catch (e) {}
const actions = rows.filter(function (r) { return r.kind === 'Action'; });
const needs = actions.filter(function (r) { return r.allocation === 'Needs Brad'; }).length;
const failed = made.filter(function (r) { return !r.id || r.object === 'error'; }).length;
const meetings = rows.filter(function (r) { return r.kind === 'Meeting summary'; }).length;
return [{ json: {
  run: 'hq-meeting-actions ' + DateTime.now().setZone('Australia/Sydney').toFormat('yyyy-LL-dd HH:mm'),
  tool: 'hq-meeting-actions (n8n + Claude)',
  requested_by: 'schedule',
  inputs: 'Wispr Flow meetings since ' + DateTime.now().minus({ days: 4 }).setZone('Australia/Sydney').toFormat('d LLL') + '; seen ' + (pickd.seen || 0) + ', skipped ' + ((pickd.skipped || []).length),
  result: failed ? 'Failed' : (drafts.length ? 'Waiting approval' : 'Success'),
  approval: drafts.length ? 'Pending' : 'Not required',
  approved_by: '',
  summary: meetings + ' meetings processed, ' + actions.length + ' actions recorded, ' + drafts.length + ' email drafts for Brad to send, ' + needs + ' actions need Brad to confirm the owner' + (failed ? ', ' + failed + ' Notion rows FAILED to save' : '') + (pickd.more_available ? '; more meetings than one page, check Wispr Flow' : ''),
  sop_version: 'no SOP yet (hq-meeting-actions page not written)',
} }];
