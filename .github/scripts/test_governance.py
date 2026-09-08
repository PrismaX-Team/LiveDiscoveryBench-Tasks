import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import json
spec = importlib.util.spec_from_file_location("governance", Path(__file__).with_name("governance.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

class GovernanceTests(unittest.TestCase):
    def proposal(self):
        schema = json.loads(Path(__file__).with_name("proposal-schema.json").read_text())
        body = "\n\n".join(f"### {f['label']}\n\n" + ("https://example.org/profile" if f['id']=='professionalUrl' else 'Research evidence') for f in schema['fields'])
        body += '\n\n### Metric type / 指标类型\n\nraw_only · Keep original'
        body += '\n\n### Permissions / 授权确认\n\n' + '\n'.join('- [X] '+c for c in schema['consents'])
        return dict(number=1, title='A scientific proposal', body=body, lastEditedAt=None, category={'slug':'proposals'}, closed=False, author={'login':'author'}, comments=[])
    def test_form_and_conditional_validation(self):
        row = self.proposal()
        g.validate_proposal(row)
        row['body'] = row['body'].replace('### Additional explanation / 补充说明\n\nResearch evidence', '### Additional explanation / 补充说明\n\n_No response_')
        with self.assertRaises(ValueError): g.validate_proposal(row)
    def test_missing_consent(self):
        row = self.proposal(); row['body'] = row['body'].replace('- [X]', '- [ ]')
        with self.assertRaises(ValueError): g.validate_proposal(row)
    def test_consent_text_outside_confirmation_is_not_consent(self):
        row = self.proposal()
        row['body'] = row['body'].replace('### Permissions / 授权确认', '### Example text')
        with self.assertRaises(ValueError): g.validate_proposal(row)
    def test_edit_then_revert_changes_digest(self):
        row = self.proposal(); before = g.digest(row); row['lastEditedAt']='2026-09-08T00:00:00Z'
        self.assertNotEqual(before, g.digest(row))
    def test_cross_repo_proposal_rejected(self):
        for body in ['Proposal: https://github.com/other/repo/discussions/1', 'Proposal: '+g.ROOT+'/issues/1', 'Proposal: '+g.ROOT+'/discussions/1\nProposal: '+g.ROOT+'/discussions/2']:
            with self.assertRaises(ValueError): g.proposal_number(body)
        self.assertEqual(g.proposal_number('Proposal: '+g.ROOT+'/discussions/1'), 1)
    def test_unapproved_cannot_pass(self):
        with self.assertRaises(ValueError): g.approved_proposal({'user':{'login':'author'}}, self.proposal())
    def test_author_and_self_approval(self):
        row=self.proposal(); record={'actor':'maintainer','decision':'approve','digest':g.digest(row)}
        with patch.object(g, 'decision_record', return_value=record):
            g.approved_proposal({'user':{'login':'author'}},row)
            with self.assertRaises(ValueError): g.approved_proposal({'user':{'login':'someone-else'}}, row)
            record['actor']='author'
            with self.assertRaises(ValueError): g.approved_proposal({'user':{'login':'author'}}, row)
    def test_edited_approval_invalid(self):
        row=self.proposal(); record={'actor':'maintainer','decision':'approve','digest':g.digest(row)}; row['body']+='\nChanged science'
        with patch.object(g,'decision_record',return_value=record):
            self.assertEqual(g.proposal_status(row)[0], 'needs_reapproval')
            with self.assertRaises(ValueError): g.approved_proposal({'user':{'login':'author'}}, row)
    def comment(self, body, author='maintainer', id=1):
        return dict(body=body,user={'login':author}, updated_at=f'2026-09-08T00:00:0{id}Z', id=id)
    def test_seats(self):
        pr={'user':{'login':'author'}}; permission=lambda login: login=='maintainer'
        for body in ['/reviewers domain=@author technical=@two', '/reviewers domain=@one technical=@one']:
            with self.assertRaises(ValueError): g.seats(pr,[self.comment(body)],permission)
        with self.assertRaises(ValueError): g.seats(pr,[self.comment('/reviewers domain=@one technical=@two','outsider')],permission)
        self.assertEqual(g.seats(pr,[self.comment('/reviewers domain=@one technical=@two')],permission),dict(domain='one',technical='two'))
        with self.assertRaises(ValueError): g.seats(pr,[self.comment('/reviewers domain=@one technical=@two'),self.comment('/reviewers revoke',id=2)],permission)
    def test_current_reviews_and_dismissal(self):
        rows=[dict(id=1,user={'login':'one'},state='APPROVED',commit_id='old')]
        self.assertFalse(g.approved_review('one',rows,'new'))
        rows.append(dict(id=2,user={'login':'one'},state='APPROVED',commit_id='new'))
        self.assertTrue(g.approved_review('one',rows,'new'))
        self.assertFalse(g.approved_review('two',rows,'new'))
        rows.append(dict(id=3,user={'login':'one'},state='COMMENTED',commit_id='new'))
        self.assertTrue(g.approved_review('one',rows,'new'))
        rows[1]['state']='DISMISSED'
        self.assertFalse(g.approved_review('one',rows,'new'))
    def test_forged_bot_record_and_api_failure(self):
        row=self.proposal(); data=dict(run='1',actor='maintainer',discussion=1,decision='approve',digest=g.digest(row))
        row['comments']=[dict(author={'login':'github-actions[bot]'}, lastEditedAt=None, createdAt='2026-09-08T01:00:00Z', body=g.MARKER+json.dumps(data)+' -->')]
        g._run_cache.clear()
        with patch.object(g,'api',return_value={'path':'.github/workflows/forged.yml'}): self.assertIsNone(g.decision_record(row))
        g._run_cache.clear()
        with patch.object(g,'api',side_effect=RuntimeError('unavailable')):
            with self.assertRaises(RuntimeError): g.decision_record(row)
    def test_acceptance_excluded(self):
        self.assertTrue(g.acceptance(dict(title='[ACCEPTANCE] Test',labels=[])))
        self.assertTrue(g.acceptance(dict(title='Test',labels={'nodes':[{'name':'acceptance'}]})))

if __name__ == '__main__': unittest.main()
