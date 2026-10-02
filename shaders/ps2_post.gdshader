shader_type canvas_item;
// PS2-era look: film grain, vignette, Bayer-dithered 16-bit-ish color quantization.

uniform sampler2D screen : hint_screen_texture, filter_nearest;
uniform float grain = 0.07;
uniform float vignette = 0.6;
uniform float levels = 32.0;

float rand(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec3 c = texture(screen, SCREEN_UV).rgb;
	c += (rand(FRAGCOORD.xy + fract(TIME) * 97.0) - 0.5) * grain;
	vec2 d = SCREEN_UV - 0.5;
	c *= 1.0 - dot(d, d) * vignette * 2.0;
	const float bayer[16] = float[](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	ivec2 p = ivec2(FRAGCOORD.xy) % 4;
	float t = bayer[p.y * 4 + p.x] / 16.0;
	c = floor(c * levels + t) / levels;
	COLOR = vec4(c, 1.0);
}
