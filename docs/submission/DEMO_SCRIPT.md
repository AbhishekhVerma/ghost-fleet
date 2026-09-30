# Demo script and video shot list (3 minutes)

Use the same script for the live pitch demo and the recorded video.

**Before you start**
- Open https://ghost-fleet.vercel.app in a clean browser window at about
  1440×900. Zoom 100%, bookmarks bar hidden.
- In a second tab, open https://ghost-fleet.vercel.app/#imo=9240885 as a backup.
- Recording: OBS or the Windows Game Bar (Win+Alt+R). Use a headset mic and a
  quiet room. Move the mouse slowly and pause about one second after each click.

---

## 0:00–0:20 · The hook

**Screen:** the overview, untouched. Let the map sit.

> "A ship can turn off its beacon, but it cannot stop leaving a trail.
> Since 2022, a shadow fleet of old tankers has kept sanctioned Russian oil
> flowing by changing names, flags and radio identities. Oil traders need to
> know one thing: is that hidden supply growing or shrinking?"

**Caption:** *Ghost Fleet — hidden oil supply, seen from the sea*

## 0:20–0:50 · The answer first

**Screen:** point the cursor at the headline, then run along the bars from
March to August.

> "Ghost Fleet answers that in one line. Across 300 of the most-sanctioned
> shadow-fleet tankers, activity fell 10% over the last three months. That's
> June to August against March to May, the dark bars against the grey ones.
> Every number comes from public data: OpenSanctions for who is sanctioned,
> Global Fishing Watch for what those ships actually did."

**Caption:** *−10% active sanctioned tankers, Jun–Aug vs Mar–May*

## 0:50–1:15 · Where it is moving

**Screen:** scroll the panel to *Busiest ports of call*, then sweep the cursor
across the map from the Baltic to the Black Sea, Suez and the Russian Far East.

> "Where are they going? Nakhodka in the Pacific, Primorsk and Ust-Luga on the
> Baltic, through Suez and Port Said. Those are Russia's export routes, and
> they came straight out of the data. We didn't draw them in."

## 1:15–2:10 · One ship's story (the key moment)

**Screen:** type `longevity` in the vessel search and click **Wolf**. The map
zooms to its activity. Slowly point down the numbered identity list.

> "Now search a name this ship used last year, Longevity 7. We get
> today's Wolf. Same hull, same IMO number. It started life as the Danish
> Torm Gertrud. Then it became East 1 in Hong Kong, Longevity 7 in Palau,
> then Wolf under the flag of Malawi, a country with no coastline.
> Three weeks ago it switched again, to Aruba. Seven identities."

**Screen:** point at the score breakdown, then at *Recent activity*.

> "Its score of 75 isn't a black box. Forty points for the sanctions listings,
> thirty for the identity switches, five for loitering at sea. It idled
> offshore for up to two weeks at a time this summer, the kind of pattern you
> see with floating storage or ship-to-ship transfers."

**Caption:** *7 identities · 7 flags · 1 hull*

## 2:10–2:35 · Honesty as a feature

**Screen:** scroll to *Size and value*, then the disclaimer.

> "We're strict about what the data can't tell us. Public tracking has no
> draft readings, so we don't guess whether this ship is loaded. We say
> unknown. Values are ranges with their assumptions shown. A listing or a
> score is a lead for an analyst, not proof."

## 2:35–3:00 · Close

**Screen:** click **Back to overview**. The whole fleet reappears.

> "Across these 300 ships we found 81 different flags, and eleven are
> flagged to landlocked countries today. Next, we screen all 892 listed
> vessels daily and add licensed draft data, to turn this activity signal
> into barrels. Ghost Fleet: the hidden fleet, made visible."

**End card:** *ghost-fleet.vercel.app · github.com/aaaditt/ghost-fleet*

---

## If something breaks live

- **The map tiles are slow:** keep talking. The panel and dossier don't
  depend on the tiles.
- **The site is unreachable:** run it locally with
  `cd dashboard; python -m http.server 8765`, then open `localhost:8765`.
- **Someone asks "is this live?"** "It's a dated snapshot, 30 September 2025
  to 27 September 2026. Refreshing it is one command."

## Likely judge questions

| Question | Answer |
|---|---|
| Is this AI? | "It's a data-fusion and scoring pipeline, not a trained model. We chose a transparent score because a trader or compliance user has to be able to explain it. A trained loaded/ballast model needs draft data we don't have for free." |
| How accurate is it? | "We don't claim accuracy yet. Every input is sourced and dated, and the trend is hand-checked. Validation against published export estimates is the next step." |
| Why did activity fall? | "The tool shows *that* it fell, not why. Possible reasons include enforcement, seasonality and ships moving to identities we haven't screened. That's exactly what an analyst would investigate next." |
| Can you see ship-to-ship transfers? | "Not directly. Free tracking data has no tanker-to-tanker encounters, so we show long idle periods at sea as the observable proxy and label them that way." |
| Business model? | "A data feed and alerting for commodity desks and compliance teams, with licensed AIS and sanctions data. The free sources we used are non-commercial." |
