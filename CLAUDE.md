# TBOI Tears Test

Sito web statico che mostra come cambia l'attacco di Isaac (The Binding of Isaac) combinando più oggetti, con un'anteprima animata dello sparo.

## Regole del progetto

- **Mai inventare sinergie.** Ogni regola o interazione deve avere una `fonte`: link alla pagina della wiki (https://bindingofisaacrebirth.wiki.gg) e frase da cui è stata ricavata.
- **Versione di riferimento: Repentance+.** Nella wiki i tag `{{Dlc|...}}` indicano la versione: scartare le informazioni valide solo per versioni precedenti.
- Se due pagine della wiki si contraddicono, salvare entrambe le versioni e segnalare il conflitto nel sito, senza sceglierne una.
- Valori numerici (frame, velocità, angoli) usati nell'animazione: presi dalla wiki quando ci sono; se sono stimati, marcarli come `stimato`.

## Oggetti inclusi

- Dentro: oggetti che cambiano **tipo, comportamento, effetto o numero** dei colpi dell'attacco principale (incluse armi che sostituiscono le lacrime, es. Brimstone, Mom's Knife). Inclusi anche oggetti "di statistica" che cambiano il comportamento dell'attacco (es. Soy Milk, Chocolate Milk).
- Fuori: oggetti che cambiano solo valori numerici (danno, fire rate, gittata, shot speed), cuori, consumabili, oggetti attivi non legati allo sparo.
- Fuori: famigli, anche quelli che copiano le lacrime (Incubus, Twisted Pair, ...).

## Categorie di effetto

- `sostituisce`: cambia l'arma (Brimstone, Mom's Knife, Dr. Fetus, Tech X, ...)
- `aggiunge`: aggiunge un effetto alle lacrime (homing, piercing, veleno, split, ...)
- `moltiplica`: cambia il numero di colpi (20/20, Inner Eye, Mutant Spider, ...)
- `eccezione`: interazione specifica tra due o più oggetti (dalle sezioni Synergies/Interactions della wiki)
