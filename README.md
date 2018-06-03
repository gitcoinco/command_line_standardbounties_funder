# StandardBounties CLI Funder

This cli tool is being built for @owocki.

## Example Usage

In order to start using the CLI tool you'll need to make a `secrets.json` file in the root directory of this repo with the schema below. Update the `mnemonic` key with the mnemonic you want to use to fund your bounties.

```
{
  "mnemonic" : "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
}
```

**Interactive Mode**
```
python3 src/main.py https://github.com/gitcoinco/command_line_standardbounties_funder/issues/1 0.01
```

**JSON Mode**

```
python3 src/main.py --json data.json
```

`data.json`:

``` json
{
    "issueURL": "https://github.com/gitcoinco/command_line_standardbounties_funder/issues/1",

    "githubUsername": "c-o-l-o-r",

    "title": "Bounty funder CLI",
    "description": "We want a way for people to fund bounties from the command line using Python.",
    "keywords": [ "command_line_standardbounties_funder", "gitcoinco" ],
    "experienceLevel": "Intermediate",
    "projectLength": "Hours",
    "bountyType": "Feature",
    "expireDate": 1530480195,

    "notificationEmail": "mattgarnett@ucla.edu",
    "fullName": "Matt Garnett",

    "showEmailPublicly": false,
    "showNamePublicly": false,

    "amount": 0.01,
    "tokenName": "ETH"
}
```
