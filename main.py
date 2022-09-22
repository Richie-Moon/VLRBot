import discord
from discord import app_commands, ui
import requests
import json
from os import environ
from dotenv import load_dotenv
import datetime
import zoneinfo


# Put into requirements:
# import tzdata


def convert_to_unix(time_data: str):
    dt_now = datetime.datetime.now(tz=zoneinfo.ZoneInfo('Pacific/Auckland'))

    if 'd' in time_data:
        contains_d = True
    else:
        contains_d = False

    time_data = time_data.split()

    if len(time_data) == 3:
        time_data.pop(-1)
        for item in time_data:
            if len(item) == 3:
                if item[2] == 'w':
                    dt_now -= datetime.timedelta(weeks=float(item[0:2]))
                elif item[2] == 'd':
                    dt_now -= datetime.timedelta(days=float(item[0:2]))
                elif item[2] == 'h':
                    dt_now -= datetime.timedelta(hours=float(item[0:2]))
                elif item[2] == 'm':
                    dt_now -= datetime.timedelta(minutes=float(item[0:2]) - 1)
                elif item[2] == 's':
                    dt_now -= datetime.timedelta(seconds=float(item[0:2]))
            elif len(item) == 2:
                if item[1] == 'w':
                    dt_now -= datetime.timedelta(weeks=float(item[0]))
                elif item[1] == 'd':
                    dt_now -= datetime.timedelta(days=float(item[0]))
                elif item[1] == 'h':
                    dt_now -= datetime.timedelta(hours=float(item[0]))
                elif item[1] == 'm':
                    dt_now -= datetime.timedelta(minutes=float(item[0]))
                elif item[1] == 's':
                    dt_now -= datetime.timedelta(seconds=float(item[0]))

    elif len(time_data) == 4:
        for i in range(2):
            time_data.pop(-1)

        for item in time_data:
            if len(item) == 3:
                if item[2] == 'w':
                    dt_now += datetime.timedelta(weeks=float(item[0:2]))
                elif item[2] == 'd':
                    dt_now += datetime.timedelta(days=float(item[0:2]))
                elif item[2] == 'h':
                    dt_now += datetime.timedelta(hours=float(item[0:2]))
                elif item[2] == 'm':
                    dt_now += datetime.timedelta(minutes=float(item[0:2]))
                elif item[2] == 's':
                    dt_now += datetime.timedelta(seconds=float(item[0:2]))
            elif len(item) == 2:
                if item[1] == 'w':
                    dt_now += datetime.timedelta(weeks=float(item[0]))
                elif item[1] == 'd':
                    dt_now += datetime.timedelta(days=float(item[0]))
                elif item[1] == 'h':
                    dt_now += datetime.timedelta(hours=float(item[0]))
                elif item[1] == 'm':
                    dt_now += datetime.timedelta(minutes=float(item[0]) + 1)
                elif item[1] == 's':
                    dt_now += datetime.timedelta(seconds=float(item[0]))

    if contains_d is True:
        return int(datetime.datetime.strptime(str(dt_now.date()), '%Y-%m-%d').timestamp()), True
    else:
        return int(datetime.datetime.timestamp(dt_now)), False


load_dotenv()
token = environ['TOKEN']

guilds = [discord.Object(id=716770439862681620), discord.Object(id=792309472784547850)]


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=guilds[1])
            self.synced = True
        print(f"Logged in as {self.user}")


client = aclient()
tree = app_commands.CommandTree(client)


# class Questionnaire(ui.Modal, title="Questionnaire"):
#     name = ui.TextInput(label='Name')
#     answer = ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)
#
#     async def on_submit(self, interaction: discord.Interaction):
#         await interaction.response.send_message(f'Thanks for your response,'
#                                                 f' {self.name}!',
#                                                 ephemeral=True)


class Matches(ui.Select):
    """Takes the tournament name as an argument and finds all the matches from that tournament.
    Sends that list to the user in a dropdown menu. """

    def __init__(self, name, url_type):
        self.name = name
        self.url_type = url_type
        if self.url_type == 'results':
            self.get = requests.get('https://vlrggapi.vercel.app/match/results').text
        else:
            self.get = requests.get('https://vlrggapi.vercel.app/match/upcoming').text
        self.data = json.loads(self.get)['data']['segments']

        self.matches = []

        count = 0
        for match in self.data:
            if count != 25:
                if match['tournament_name'] == self.name:
                    self.matches.append(match)
                    count += 1
            else:
                break

        options = []
        for option in self.matches:
            options.append(discord.SelectOption(label=f"{option['team1']} vs {option['team2']}",
                                                description=option['round_info'],
                                                value=str(self.matches.index(option))))

        super().__init__(placeholder='Select Match', options=options)

    async def callback(self, interaction: discord.Interaction):
        match = self.matches[int(self.values[0])]

        if self.url_type == 'results':
            unix, include_time = convert_to_unix(match['time_completed'])
            embed = discord.Embed(color=discord.Color.from_rgb(138, 43, 226),
                                  timestamp=interaction.created_at,
                                  title=f"{match['team1']} vs {match['team2']}")

            if int(match['score1']) > int(match['score2']):
                embed.add_field(name=f"Result:",
                                value=f"**:{match['flag1']}: {match['team1']} {match['score1']}**:"
                                      f"{match['score2']} {match['team2']} :{match['flag2']}:",
                                inline=True)
                if include_time is True:
                    embed.add_field(name="Info:", value=f"**Winner:** {match['team1']}"
                                                        f"\n**Round: ** {match['round_info']}"
                                                        f"\n**Time:** <t:{unix}> (<t:{unix}:R>)"
                                                        f"\n**Site:** https://vlr.gg{match['match_page']}",
                                    inline=False)
                elif include_time is False:
                    embed.add_field(name="Info:", value=f"**Winner:** {match['team1']}"
                                                        f"\n**Round: ** {match['round_info']}"
                                                        f"\n**Time:** <t:{unix}> (<t:{unix}:R>)"
                                                        f"\n**Site:** https://vlr.gg{match['match_page']}",
                                    inline=False)
            else:
                embed.add_field(name=f"Result:",
                                value=f":{match['flag1']}: {match['team1']} {match['score1']}:"
                                      f"**{match['score2']} {match['team2']} :{match['flag2']}:**",
                                inline=True)
                if include_time is True:
                    embed.add_field(name='Info:', value=f"**Winner:** {match['team2']}"
                                                        f"\n**Round: ** {match['round_info']}"
                                                        f"\n**Time:** <t:{unix}> (<t:{unix}:R>)"
                                                        f"\n**Site:** https://vlr.gg{match['match_page']}"
                                                        f"\n", inline=False)
                elif include_time is False:
                    embed.add_field(name='Info:', value=f"**Winner:** {match['team2']}"
                                                        f"\n**Round: ** {match['round_info']}"
                                                        f"\n**Time:** <t:{unix}:D> (<t:{unix}:R>)"
                                                        f"\n**Site:** https://vlr.gg{match['match_page']}"
                                                        f"\n", inline=False)

            embed.set_author(icon_url=match['tournament_icon'], name=match['tournament_name'])
            await interaction.response.send_message(embed=embed)

        else:
            unix, include_time = convert_to_unix(match['time_until_match'])
            embed = discord.Embed(colour=discord.Color.from_rgb(255, 87, 51),
                                  timestamp=interaction.created_at,
                                  title=f"{match['team1']} vs {match['team2']}")
            embed.set_author(icon_url=match['tournament_icon'], name=match['tournament_name'])

            if include_time is True:
                embed.add_field(name="Info:", value=f"\n**Round: ** {match['round_info']}"
                                                    f"\n**Time:** <t:{unix}> (<t:{unix}:R>)"
                                                    f"\n**Site:** https://vlr.gg{match['match_page']}")
            elif include_time is False:
                embed.add_field(name="Info:", value=f"\n**Round: ** {match['round_info']}"
                                                    f"\n**Time:** <t:{unix}:D> (<t:{unix}:R>)"
                                                    f"\n**Site:** https://vlr.gg{match['match_page']}")
            await interaction.response.send_message(embed=embed)


class Tournaments(ui.Select):
    """Gets a list of recent tournaments and sends all the options in a dropdown menu. """

    def __init__(self, url_type: str):
        self.url_type = url_type
        if self.url_type == 'results':
            self.get = requests.get('https://vlrggapi.vercel.app/match/results').text
        else:
            self.get = requests.get('https://vlrggapi.vercel.app/match/upcoming').text
        self.data = json.loads(self.get)

        count = 0
        tournament_names = []
        tournaments = []
        for match in self.data['data']['segments']:
            if count != 25:
                option = match['tournament_name']
                if option in tournament_names:
                    pass
                else:
                    tournament_names.append(option)
                    count += 1
            else:
                break

        for tournament in tournament_names:
            tournaments.append(discord.SelectOption(label=tournament))

        super().__init__(placeholder="Select Tournament", options=tournaments)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=MatchView(name=self.values[0], url_type=self.url_type))


class TournamentView(ui.View):
    def __init__(self, *, timeout=None, url_type):
        super().__init__(timeout=timeout)
        self.add_item(Tournaments(url_type=url_type))


class MatchView(ui.View):
    def __init__(self, name, *, timeout=15, url_type: str):
        super().__init__(timeout=timeout)
        self.add_item(Matches(name=name, url_type=url_type))


@tree.command(guilds=guilds)
async def test(interaction: discord.Interaction, number: int, string: str):
    await interaction.response.send_message(f'{number=} {string=}',
                                            ephemeral=False)


@tree.command(guilds=guilds)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'{round(client.latency * 1000)}ms')


# @tree.command(guilds=guilds)
# async def modal(interaction: discord.Interaction):
#     await interaction.response.send_modal(Questionnaire())


@tree.command(guilds=guilds)
async def results(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(view=TournamentView(url_type='results'))


@tree.command(guilds=guilds)
async def upcoming(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(view=TournamentView(url_type='upcoming'))


@tree.command(guilds=guilds)
async def account(interaction: discord.Interaction, name: str, tag: str):
    await interaction.response.defer()
    all_data = json.loads(requests.get(f'https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}').text)
    if all_data['status'] == 200:
        data = all_data['data']
        embed = discord.Embed(colour=discord.Color.from_rgb(148, 0, 211), timestamp=interaction.created_at,
                              title=f"Profile for {data['name']}")
        embed.set_author(name=f"{data['name']}#{data['tag']}", icon_url=data['card']['small'])
        embed.set_image(url=data['card']['wide'])
        embed.add_field(name="Level", value=data['account_level'])

        embed.set_footer(text='Last updated ' + data['last_update'])
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("Fetch failed. I will add more detail later but i cant be bothered rn. ")


class UserMatches(ui.Select):
    def __init__(self, name, tag, gamemode):

        if gamemode:
            self.data = json.loads(requests.get(f'https://api.henrikdev.xyz/valorant/v3/matches/ap/{name}/{tag}?filter={gamemode}').text)
        else:
            self.data = json.loads(requests.get(f'https://api.henrikdev.xyz/valorant/v3/matches/ap/{name}/{tag}').text)

        if self.data['status'] == 200:
            self.data = self.data['data']
        else:
            print(self.data['status'])

        self.matches = []
        self.raw_matches = []

        for match in self.data:
            match.pop('rounds')
            match.pop('kills')
            self.raw_matches.append(match)
            for player in match['players']['all_players']:
                if player['name'].lower() == name.lower():
                    self.team = player['team'].lower()
            self.matches.append(discord.SelectOption(label=f"{match['metadata']['map']} {match['teams'][self.team]['rounds_won']}-{match['teams'][self.team]['rounds_lost']}",
                                                     value=match['metadata']['game_start']))

        super().__init__(placeholder='Match', options=self.matches, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        for match in self.raw_matches:
            if match['metadata']['game_start'] == self.values[0]:
                if match['teams'][self.team]['rounds_won'] > match['teams'][self.team]['rounds_lost']:
                    colour = discord.Color.from_rgb(0, 0, 255)
                elif match['teams'][self.team]['rounds_won'] < match['teams'][self.team]['rounds_lost']:
                    colour = discord.Color.from_rgb(255, 0, 0)
                else:
                    colour = discord.Color.from_rgb(128, 128, 128)

                embed = discord.Embed(colour=colour, timestamp=interaction.created_at, title=f"{match['metadata']['map']} "
                                                                                             f"{match['teams'][self.team]['rounds_won']}-{match['teams'][self.team]['rounds_lost']}")

                team_players = []
                enemy_players = []
                rounds_played = match['metadata']['rounds_played']
                if self.team == 'red':
                    for player in match['players']['red']:
                        team_players.append({'name': player['name'], 'rank': player['currenttier_patched'], 'acs': player['stats']['score']//rounds_played, 'kills': player['stats']['kills'], 'deaths': player['stats']['deaths'],
                                             'assists': player['stats']['assists'], 'adr': round(player['damage_made']/rounds_played, 2)})
                else:
                    for player in match['players']['blue']:
                        enemy_players.append({'name': player['name'], 'rank': player['currenttier_patched'], 'acs': player['stats']['score']//rounds_played, 'kills': player['stats']['kills'], 'deaths': player['stats']['deaths'],
                                             'assists': player['stats']['assists'], 'adr': round(player['damage_made']/rounds_played, 2)})

                sorted_team_players = sorted(team_players, key=lambda sort: sort['acs'], reverse=True)
                sorted_enemy_players = sorted(enemy_players, key=lambda sort: sort['acs'], reverse=True)

                for player in sorted_team_players:
                    embed.add_field(name=player['name'], value=f"ACS: {player['acs']}, Kills: {player['kills']}, Deaths: {player['deaths']}, Assists: {player['assists']}, ADR: {player['adr']}")

                await interaction.followup.send(embed=embed)


class UserMatchView(ui.View):
    def __init__(self, name, tag, gamemode, *, timeout=15):
        super().__init__(timeout=timeout)
        self.add_item(UserMatches(name=name, tag=tag, gamemode=gamemode))


@tree.command(guilds=guilds)
async def history(interaction: discord.Interaction, name: str, tag: str, gamemode: str = None):
    await interaction.response.defer()

    await interaction.followup.send(view=UserMatchView(name=name, tag=tag, gamemode=gamemode))


client.run(token)
