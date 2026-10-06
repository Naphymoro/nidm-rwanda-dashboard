"""Synthetic datasets for the guided tour: four topics, each with a simple and a thought-provoking version.

Every record is invented for teaching (consent "synthetic") and says so. The simple version shows the journey working;
the thought-provoking one is written to make the tool's limits visible: a trusted messenger repeating a rumour, a
negation the keyword encoder misreads ("I do not trust" still counts "trust"), mixed feelings, and a Kinyarwanda note
with an English translation. The Kinyarwanda was written for teaching and should be checked by a speaker before it is
used as an example of real speech.

The keyword encoder's word lists were built for clean cooking (encoding.KEYWORDS). On the other topics it picks up only
the general trust, rumour, cost, health, social and feeling words, and the tour says so.
"""

PERIOD = '2026-Q2'
TRANSLATION_NOTE = 'Synthetic example (translation not checked by a person)'


def _records(*rows):
    out = []
    for index, row in enumerate(rows, 1):
        text, place = row[0], row[1]
        record = {'text': text, 'admin_unit': place, 'source_name': f'Synthetic interview {index}', 'period': PERIOD,
                  'consent': 'synthetic', 'language': 'en'}
        if len(row) > 2:
            record.update(language='rw', translation_en=row[2], translation_checked_by=TRANSLATION_NOTE)
        out.append(record)
    return out


DATASETS = [
    {'id': 'cooking-simple', 'topic': 'Clean cooking', 'level': 'simple',
     'title': 'Trusted messengers and improved stoves',
     'summary': 'Three households weigh the price of an improved stove against what a trusted health worker showed them.',
     'question': 'How might trusted messengers change clean cooking adoption?',
     'records': _records(
         ('Households in Niboye say the improved stoves save charcoal and they trust the health worker who showed them, '
          'but the price is too high and some neighbours heard a rumour that the smoke makes food taste bad.', 'Kicukiro / Niboye'),
         ('In Gatenga the cooperative leader explained the subsidy, yet families worry about repair costs and whether spare '
          'parts can be found nearby. Several said they would adopt if a neighbour they trust used one first.', 'Kicukiro / Gatenga'),
         ('A mother in Kimironko said the new stove helped: less smoke in the kitchen, her children cough less, and cooking '
          'is faster. She showed it at the women\'s group meeting and two families asked where to buy one.', 'Gasabo / Kimironko')),
     'twin': {'obs': 0.2, 'trust': 0.0, 'barrier': 0.05},
     'notice': 'Look at which words moved each score: "trust", "showed" and "health worker" raise trust; "price", '
               '"repair" and "rumour" raise barriers.'},
    {'id': 'cooking-provoking', 'topic': 'Clean cooking', 'level': 'thought-provoking',
     'title': 'When the trusted messenger repeats the rumour',
     'summary': 'A respected health worker passes on an explosion rumour; trust and fear arrive through the same person.',
     'question': 'Why might clean cooking stall even where people trust the messengers?',
     'records': _records(
         ('Everyone here trusts our health worker, and last week she told the women\'s group she had heard that gas '
          'cylinders can explode in a hot kitchen. Since then nobody in our village wants to try one.', 'Musanze / Muhoza'),
         ('I do not trust the subsidy to last. They gave us cheap stoves two years ago and then the price of spare parts '
          'doubled. People say it was a trick to sell us something we cannot afford to repair.', 'Huye / Ngoma'),
         ('Charcoal sellers in the market say the clean stoves will take their income. They warn customers that the food '
          'tastes different and that the stoves break in the rainy season. Many buyers believe them.', 'Rubavu / Gisenyi'),
         ('My neighbour has used an LPG stove for a year without any problem. She cooks faster and saves money, but when I '
          'told my family, my husband said it is not our tradition and we should not change.', 'Kicukiro / Gatenga')),
     'twin': {'obs': 0.12, 'trust': -0.05, 'barrier': 0.08},
     'notice': 'Record 1 raises trust only through "health worker" (the lists have "trust" and "trusted" but not "trusts") '
               'while "heard" and "explode" count as rumour words. Record 2 says "I do not trust" and still counts "trust". '
               'In record 3, "many buyers believe them" counts "believe" as a trust word although they believe a rumour. '
               'A human reader sees a trusted messenger spreading fear; counting words cannot.'},
    {'id': 'transition-simple', 'topic': 'Just transition', 'level': 'simple',
     'title': 'Moving away from charcoal, fairly',
     'summary': 'A charcoal producer, a cooperative leader and a women\'s group talk about who gains and who loses.',
     'question': 'How might a fair transition plan change support for moving away from charcoal?',
     'records': _records(
         ('I have made charcoal for twenty years and it feeds my family. If charcoal is banned I am afraid we will have no '
          'income. I would support the change if there were training and a loan to start another trade.', 'Nyagatare / Nyagatare'),
         ('Our cooperative leader explained a plan to train charcoal makers as stove technicians and solar installers. '
          'People trust him because he helped with the coffee cooperative, so many members signed up.', 'Nyamagabe / Gasaka'),
         ('The women\'s group says cleaner fuel means less smoke and less time collecting wood. They hope the transition '
          'plan includes payment by installments so poorer families are not left behind.', 'Muhanga / Nyamabuye')),
     'twin': {'obs': 0.18, 'trust': 0.02, 'barrier': 0.04},
     'notice': 'The encoder knows "charcoal", "wood", "fuel", "loan" and "payment" from clean cooking, so this topic still '
               'gets cost and fuel signals. It has no words for jobs or fairness, so those themes stay invisible.'},
    {'id': 'transition-provoking', 'topic': 'Just transition', 'level': 'thought-provoking',
     'title': 'Who carries the cost of a charcoal ban?',
     'summary': 'Traders, technicians and rumours about who benefits: fairness stories that can turn people against the change.',
     'question': 'Who carries the cost when a city bans charcoal, and how might their stories shape support for the transition?',
     'records': _records(
         ('Since the ban was announced, traders in our market say it is a plan by big companies to sell expensive gas. '
          'Some say the officials will profit. People repeat it at every meeting and nobody checks if it is true.', 'Kigali / Nyabugogo'),
         ('We heard the jobs promised in solar went to young people from the city, not to us. My cousin finished the '
          'training but nobody hired him. Now people in the village doubt every promise about the transition.', 'Rusizi / Kamembe'),
         ('I trained as a stove technician last year. Now I repair stoves for half the sector and earn more than I did '
          'selling charcoal. Customers trust me because they know me, but they still fear the price of gas.', 'Huye / Tumba'),
         ('Twebwe abacuruza amakara turibaza aho tuzakura amafaranga niba amakara abujijwe. Abana bacu bakeneye ishuri.', 'Rwamagana / Kigabiro',
          'We charcoal sellers wonder where we will find money if charcoal is banned. Our children need school fees.'),
         ('A teacher said the transition is good for the children\'s health because there is less smoke, but parents in '
          'her class worry more about food prices than about air. They believe the change helps only the rich.', 'Gasabo / Remera')),
     'twin': {'obs': 0.1, 'trust': -0.04, 'barrier': 0.1},
     'notice': 'Fairness stories ("helps only the rich", "jobs went to the city") are about trust in the process, yet the '
               'encoder has no fairness words. Record 4 is in Kinyarwanda: the scores read its English translation, and the '
               'gate asks you to check that translation before accepting.'},
    {'id': 'ai-simple', 'topic': 'AI in the classroom', 'level': 'simple',
     'title': 'Parents, teachers and an AI tutor',
     'summary': 'Parents decide about an AI tutoring app after a teacher demonstrates it.',
     'question': 'How might teacher demonstrations change parents\' acceptance of AI tutors in schools?',
     'records': _records(
         ('At the parents\' meeting the teacher showed us the AI tutor on a tablet. My son answered maths questions and '
          'the app explained his mistakes. I trust the teacher, so I am willing to let him use it.', 'Gasabo / Kimironko'),
         ('Parents in our sector worry about the cost of tablets and data. The school leader said the government may help, '
          'but families who cannot afford a phone at home fear their children will fall behind.', 'Bugesera / Nyamata'),
         ('A girl in senior two said the tutor helped her prepare for exams faster, and she benefits from practising at '
          'her own pace. Her classmates asked the teacher to use it in the next term.', 'Huye / Ngoma')),
     'twin': {'obs': 0.25, 'trust': 0.03, 'barrier': 0.04},
     'notice': 'Words like "showed", "trust", "leader", "cost" and "afford" carry over from clean cooking; "tablet", '
               '"exam" and "teacher" are not in any list, so they do not change the scores.'},
    {'id': 'ai-provoking', 'topic': 'AI in the classroom', 'level': 'thought-provoking',
     'title': 'Will AI widen the gap between schools?',
     'summary': 'Rural schools without power, a replacement rumour, and teachers who fear being watched.',
     'question': 'Could AI tutors widen the gap between schools, and what stories might shape that?',
     'records': _records(
         ('Our school has no electricity, so the tablets stay locked in a cupboard. Parents heard that schools in the '
          'city use AI every day, and they say our children are being left behind again.', 'Nyaruguru / Kibeho'),
         ('People say the AI will replace teachers and the government will close the training college. A rumour on the '
          'radio claimed half the teachers would lose their jobs. Teachers here are afraid and angry.', 'Karongi / Bwishyura'),
         ('I do not trust an app that records what my pupils write. Who reads it? The head teacher says it is safe, but '
          'nobody explained where the data goes, and some parents refused to sign the form.', 'Musanze / Muhoza'),
         ('Students say the AI helps them finish homework quickly, but some copy the answers without learning. One '
          'teacher found three identical essays and now doubts the tool is helping anyone.', 'Kicukiro / Gatenga')),
     'twin': {'obs': 0.15, 'trust': -0.06, 'barrier': 0.07},
     'notice': 'Record 3 says "I do not trust" and the encoder still counts "trust". The equity story in record 1 '
               '(no electricity, left behind) is read only as a fuel word ("electricity") and a rumour word ("heard"), '
               'so the scores miss the main point. Record 4 (copying answers) matches no list at all.'},
    {'id': 'vaccine-simple', 'topic': 'Vaccines', 'level': 'simple',
     'title': 'Community health workers and the HPV vaccine',
     'summary': 'Mothers decide about the HPV vaccine for their daughters after talking with community health workers.',
     'question': 'How might community health workers change trust in the HPV vaccine?',
     'records': _records(
         ('The community health worker visited our home and explained the HPV vaccine protects girls from cancer later in '
          'life. I trust her because she helped when my child was sick, so my daughter will get it.', 'Gasabo / Kimironko'),
         ('At the market I heard a rumour that the vaccine makes girls unable to have children. Some mothers believe it, '
          'and they will wait until a health worker they know explains it at the village meeting.', 'Rwamagana / Kigabiro'),
         ('The health centre is far from our village and the trip costs money, so some families delay. If the vaccine '
          'were given at school, parents say more girls would receive it.', 'Nyaruguru / Kibeho')),
     'twin': {'obs': 0.55, 'trust': 0.02, 'barrier': 0.03},
     'notice': '"Health worker", "trust", "children" and "health" raise trust; "rumour" and "heard" lower it and '
               '"money" raises barriers ("costs" is not in the lists, only "cost"). In record 2, "some mothers believe it" '
               'counts "believe" as a trust word although they believe the rumour. The encoder has no vaccine words.'},
    {'id': 'vaccine-provoking', 'topic': 'Vaccines', 'level': 'thought-provoking',
     'title': 'When a respected leader repeats a vaccine rumour',
     'summary': 'A church leader, a video on a phone, and a mother who trusts the nurse but not the vaccine.',
     'question': 'What happens when a trusted local leader repeats a vaccine rumour?',
     'records': _records(
         ('Our church leader is respected by everyone. On Sunday he said he had heard the vaccine was tested on African '
          'girls first and may harm them. Many families decided to wait, even those who trust the clinic.', 'Rubavu / Gisenyi'),
         ('I do not trust the vaccine, but I trust the nurse at our health centre. She has looked after my family for '
          'years. If she tells me herself that it is safe, I will think about it again.', 'Huye / Tumba'),
         ('A video on a phone is going around the village showing a girl who fainted after an injection. Nobody knows '
          'where it was filmed, but people share it and say it proves the danger.', 'Nyagatare / Nyagatare'),
         ('Abantu benshi bavuga ko urukingo rutera ubugumba, ariko umujyanama w\'ubuzima yatubwiye ko atari ukuri.', 'Musanze / Muhoza',
          'Many people say the vaccine causes infertility, but the community health worker told us it is not true.'),
         ('The head teacher invited a doctor to answer parents\' questions. After the meeting some fathers who refused '
          'before accepted, because they could ask about the fainting video themselves.', 'Kicukiro / Niboye')),
     'twin': {'obs': 0.4, 'trust': -0.05, 'barrier': 0.06},
     'notice': 'Record 1 is a trusted leader spreading a rumour: trust words and rumour words in one voice. Record 2 '
               '("I do not trust the vaccine, but I trust the nurse") holds two opposite stances the encoder cannot '
               'separate. Record 5 is the kind of prebunking-by-dialogue the inoculation lab drafts.'},
]

BY_ID = {dataset['id']: dataset for dataset in DATASETS}
TOPIC_NOTE = ('NDIM\'s word lists were built for clean cooking. On other topics the encoder reads only the general trust, '
              'rumour, cost, health, social and feeling words, so read the scores as rough signals.')


def catalogue():
    return {'datasets': DATASETS, 'topic_note': TOPIC_NOTE,
            'note': 'All records are invented for teaching and marked synthetic. The Kinyarwanda notes were written for '
                    'teaching and should be checked by a speaker.'}
