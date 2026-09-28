// keep only sky-blue glass pixels of the window prop (used as a weak glow source)
shader_type canvas_item;
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	float isSky = step(c.r + 0.12, c.b) * c.a;
	COLOR = vec4(c.rgb, isSky * 0.35);
}
