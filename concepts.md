back to [Contents](Contents.md)
# Game Concepts #


## Parts ##

Ships are made of parts.  They generally have one base part (a cockpit).  Each part has zero or more **ports**, each of which another part can attach to.  As parts take damage, they have a chance of being detached from their ship.  When a part gets detached, it floats away (and any parts attached to it are also detached).  A floating part can be picked up by touching it with your ship (or by moving close to it if your ship has a Grappler part, yet to be implemented).

Generally, you can add as many parts to your ship as you want.  This can make your ship much more powerful.  As you add parts to your ship, it is important to maintain a balance: each part has a **mass**, and slows down your ship by that mass (acceleration = thrust / mass `*` pixels / second^2).  Each part also adds to the **moment of inertia** of your ship, based on it's mass and how far it is from the center of your ship (moment = sum(mass `*` distance from center) for all parts).  The higher your ship's moment, the slower it will turn (turn speed = moment / torque `*` 360 degrees / second).  Many parts also consume energy. To balance increasing energy costs you will need more generators to recover energy faster and more batteries to store more energy.  To balance more mass you will need more engines; to balance a higher moment of inertia you will need more gyroscopes.

Also, after a certain number of parts (your ship's **penalty-free** parts), each part added to your ship decreases the overall efficiency of the ship.  This number starts at 10, and can be increased by getting levels of the **modularity** skill.  Levels to the **efficiency** skill give you a bonus to efficiency for having very few parts, meaning that each part will work better than normal.

Efficiency effects:
  * Gun, Missile, and Laser damage
  * Gun and Laser range
  * Missile resupply rate
  * Engine thrust
  * Gyro torque
  * Generator generation rate
  * Battery capacity
  * Shield regeneration rate
  * Sensor range
Each of these attributes is multiplied by the efficiency of your ship (efficiency = 1.0 - penalty **extra parts + bonus** fewer parts).  You cannot have a penalty and a bonus at the same time.  levels to the organization skill reduce the penalty per part.  Generally, **Fighters** and **Interceptors** will try to maximize the efficiency of a few parts while **Destroyers** and **Dreadnoughts** will try to minimize the penalties for having lots of parts.

## The Map ##

<img src='http://i.imgur.com/IQjp7.png'>
The game is played in a "sector of the galaxy". The sector is divided into an 8x8 grid of 64 Solar Systems.  Each Solar System has a star and some number of planets.  Most of the Solar Systems are already owned by one of the Alien races, some are unclaimed, and a few are claimed by multiple races.<br>
<br>
At any time the player is in one Solar System.  When a ship flies far enough from the star in that Solar System,  it jumps through a Hyperspace tunnel to the next Solar System in that direction.<br>
<br>
<h2>Experience</h2>
The player gains general experience (the green meter on the bottom right of the screen) in many ways, including damaging enemies, destroying parts, and destroying enemy ships.  The player gains specific types of experience by performing those actions.  Thrusting Engines and turning Gyros gives movement experience, firing weapons and hitting enemies gives weapon experience, etc.<br>
<br>
Gaining a level in most skills requires both general experience and specific experience.<br>
<br>
<h2>Skills</h2>
There are a few types of skills.<br>
<ul><li>Passive skills are always in effect, e.g. giving the ship a bonus to it's thrust.<br>
</li><li>Active skills give the ship a new function it can do, without requiring an extra part.  They can be bound to a key in the <b>Keys</b> menu.<br>
</li><li>