# StandardBounties CLI Funder

This cli tool is being built for @owocki.

## Setup
In order to start using the CLI tool you'll need to make a `secrets.json` file in the root directory of this repo with the schema below. Update the `mnemonic` key with the mnemonic you want to use to fund your bounties. You can specify a different location for `secrets.json` using the `--secret` parameter.

```
{
  "mnemonic" : "candy maple cake sugar pudding cream honey rich smooth crumble sweet treat"
}
```

## Defaults
In order to make this tool as easy and configurable as possible, many arguments have default values set in the [defaults.json](funder/config/defaults.json) file. Inside there, it's possible to set defaults for things like gas price, gas limit, GitHub username, privacy settings, etc.

## Usage
For a full list of available options, run the script with the `--help` flag from the command line.

The minimum number of parameters needed to get started is just the bounty's corresponding issue URL and the amount you wish to put on the bounty.
```
python3 funder/cli.py https://github.com/gitcoinco/command_line_standardbounties_funder/issues/1 0.01
```
You should now have an interactive console come up that looks like this:

```
Github: c-o-l-o-r
Title: First bounty!
Description: This is a test bounty.
Keywords: test,bounty
Experience: beginner
Length: hours
Type: feature
```

Each of the fields from above also has corresponding flags and can be chosen directly from the command line. The following invocation will skip over asking for our Github username since it has already been provided.

```
python3 funder/cli.py https://github.com/gitcoinco/command_line_standardbounties_funder/issues/1 0.01 --github c-o-l-o-r
```

We can do even better though! The following describes a bounty the is for beginner experience levels, will only take a handful of hours to complete, and a feature type.

```
python3 funder/cli.py https://github.com/gitcoinco/command_line_standardbounties_funder/issues/1 0.01 -bhf --github c-o-l-o-r
```

Tokens can be specified using `--token GIT` where `GIT` is the token's symbol you wish to use (provided it is already in `token_list.py`) or you can use `--token-address` to specify an address of an EIP20 token you wish fund a bounty with.

```
python3 funder/cli.py a 10.1 -ahf --github c-o-l-o-r --title title --description description --keywords key,word --token-address 0x4354321ef77766e2ec327ce58d3dff8358d46208
```
