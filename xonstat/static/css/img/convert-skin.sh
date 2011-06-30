#!/bin/bash
# Generate sprites for an HTML/CSS version of a Xonotic theme
# -z- 2011
mkdir temp
mv *.tga temp
cd temp
#for i in *.tga; do convert $i ${i/%tga/png}; done
#for i in *.png; do convert $i -resize 50% web_$i; rm $i; done

for i in web_button{,gray}_{n,f,c,d}; do
	convert $i.png -gravity west -crop 25x100% $i"_1".png
	convert $i.png -gravity center -crop 50x100% $i"_2".png
	convert $i.png -gravity east -crop 25x100% $i"_3".png
	convert +append $i"_1".png $i"_2".png $i"_2".png $i"_3".png "temp_s_"$i.png
	convert +append $i"_1".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_3".png "temp_m_"$i.png
	convert +append $i"_1".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_3".png "temp_l_"$i.png
	rm $i"_1".png $i"_2".png $i"_3".png
done

for i in temp_{s,m,l}; do
	convert -append $i"_web_button"{,gray}"_"{n,f,c,d}.png z_$i.png
done
convert -append web_button{,gray}_{n,f,c,d}.png z_temp_n.png

convert +append z_temp_{n,s,m,l}.png button_sprite.png

rm temp_*
rm z_temp_*

for i in web_inputbox_{n,f}; do
	convert $i.png -gravity west -crop 25x100% $i"_1".png
	convert $i.png -gravity center -crop 50x100% $i"_2".png
	convert $i.png -gravity east -crop 25x100% $i"_3".png
	convert +append $i"_1".png $i"_2".png $i"_2".png $i"_3".png "temp_s_"$i.png
	convert +append $i"_1".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_3".png "temp_m_"$i.png
	convert +append $i"_1".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_2".png $i"_3".png "temp_l_"$i.png
	rm $i"_1".png $i"_2".png $i"_3".png
done

for i in temp_{s,m,l}; do
	convert -append $i"_web_inputbox_"{n,f}.png z_$i.png
done
convert -append web_inputbox_{n,f}.png z_temp_n.png

convert +append z_temp_{n,s,m,l}.png inputbox_sprite.png

#mv *.png ..
