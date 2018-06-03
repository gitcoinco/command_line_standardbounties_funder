from clint.textui import puts, colored, indent, prompt

def getUserInput(args):
    data = {}

    # ensure the two required arguments are there
    if( len(args.grouped.get('_')) != 2 ):
        print('invalid number of arguments')
        exit(1)

    data.update({'issueURL' : args.grouped.get('_')[0]})
    data.update({'amount'  : args.grouped.get('_')[1]})

    # validate that issueURL is a url

    # validate that amount is a number
    if( not data.get('amount').replace('.', '', 1).isdigit() ):
        print('invalid amount')


    # TODO fix error when a flag is used w/o providing an arg
    githubUsername = args.grouped.get('--githubUsername')
    data.update({ 'githubUsername' : githubUsername[0] if githubUsername else prompt.query("Please enter your GitHub username:") })

    # -- METADATA -- #
    title = args.grouped.get('--title')
    data.update({ 'title' : title[0] if title else prompt.query("Please enter a title:") })

    description = args.grouped.get('--description')
    data.update({ 'description' : description[0] if description else prompt.query("Please enter a description:") })

    # TODO ensure that keywords are split into array
    keywords = args.grouped.get('--keywords')
    data.update({ 'keywords' : keywords[0] if keywords else prompt.query("Please enter the keywords:") })

    notificationEmail = args.grouped.get('--notificationEmail')
    data.update({ 'notificationEmail' : notificationEmail[0] if keywords else prompt.query("Please enter the notification email:") })

    fullName = args.grouped.get('--fullName')
    data.update({ 'fullName' : fullName[0] if fullName else prompt.query("Please enter your full name:") })

    experienceLevel = args.grouped.get('--experienceLevel')
    data.update({ 'experienceLevel' : experienceLevel[0] if experienceLevel else prompt.query("Please enter the bounty's experience level:") })

    projectLength = args.grouped.get('--projectLength')
    data.update({ 'projectLength' : projectLength[0] if projectLength else prompt.query("Please enter the project length:") })

    bountyType = args.grouped.get('--bountyType')
    data.update({ 'bountyType' : bountyType[0] if bountyType else prompt.query("Please enter the bounty type:") })
    # -- END METADATA -- #


    # -- PRIVACY PREFERENCES -- #
    showEmailPublicly = args.grouped.get('--showEmailPublicly ')
    data.update({ 'showEmailPublicly' : True if showEmailPublicly else False })

    showNamePublicly = args.grouped.get('--showNamePublicly ')
    data.update({ 'showNamePublicly' : True if showNamePublicly else False })
    # -- END PRIVACY PREFERENCES -- #


    # -- TOKEN INFO -- #
    tokenAddress = args.grouped.get('--tokenAddress')
    data.update({ 'tokenAddress' : tokenAddress[0] if tokenAddress else '0x0000000000000000000000000000000000000000' })

    token = ''
    decimals = ''
    tokenName = ''
    decimalDivisor = ''
    # -- END TOKEN INFO #

    return json.dumps(data)
