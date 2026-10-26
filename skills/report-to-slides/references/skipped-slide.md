# Skipped-topic slide

A skipped topic keeps its place in the deck as a crossed-out frame, so the presenter sees what was left out.

## Macro (goes into the `% report-to-slides additions` block)

```latex
\usetikzlibrary{calc}
\definecolor{RTSCross}{HTML}{D62828}
\newcommand{\skipcross}{%
  \begin{tikzpicture}[remember picture,overlay]
    \coordinate (rtsTL) at ($(current page.north west)+(0.06\paperwidth,-0.25\paperheight)$);
    \coordinate (rtsBR) at ($(current page.south east)+(-0.06\paperwidth,0.13\paperheight)$);
    \draw[RTSCross,line width=8pt,line cap=round,opacity=.85]
      (rtsTL) -- (rtsBR) (rtsTL |- rtsBR) -- (rtsBR |- rtsTL);
  \end{tikzpicture}}
```

The cross spans the content area between the frame title and the footline. Adjust the two fractions only if the guideline's title or footline is taller than usual.

## Frame

```latex
\begin{frame}{<topic heading from the report>}
<one line, in report wording, naming what the topic covers>
\skipcross
\note{Skipped: <reason, e.g. multi-step math derivation>.}
\end{frame}
```

The frame sits in its report section, so the section label appears above the title. It holds only the one scope line. The topic's full content stays out of the slide and out of the note.
