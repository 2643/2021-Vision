import com.revrobotics.CANSparkMax;
import com.revrobotics.ControlType;
import com.revrobotics.CANSparkMaxLowLevel.MotorType;

import edu.wpi.first.networktables.NetworkTable;
import edu.wpi.first.networktables.NetworkTableInstance;
import edu.wpi.first.wpilibj2.command.SubsystemBase;


public class Follower
{
    private static CANSparkMax leftFrontMotor = new CANSparkMax(1, MotorType.kBrushless);
    private static CANSparkMax leftBackMotor = new CANSparkMax(2, MotorType.kBrushless);
    private static CANSparkMax rightFrontMotor = new CANSparkMax(3, MotorType.kBrushless);
    private static CANSparkMax rightBackMotor = new CANSparkMax(4 , MotorType.kBrushless);
    public static NetworkTable table = NetworkTableInstance.getDefault().getTable("datatable");
    public static void main(String[] args)
    {
        while (true)
        {
            int defaultValue = 0;
            int cx = (int) table.getEntry("Idk").getNumber(defaultValue);
            
            if (cx >= 120)

                // System.out.println("Turn Left!");
                leftFrontMotor.set(0);
                leftBackMotor.set(0);
                rightFrontMotor.set(0.3);
                rightBackMotor.set(0.3);

            else if (cx < 120 && cx > 50)

            // System.out.println("On Track")
                leftFrontMotor.set(0.3);
                leftBackMotor.set(0.3);
                rightFrontMotor.set(0.3);
                rightBackMotor.set(0.3);

            else if (cx <= 50)

            // System.out.println("Turn Right");
                leftFrontMotor.set(0.3);
                leftBackMotor.set(0.3);
                rightFrontMotor.set(0);
                rightBackMotor.set(0);

                //System.out.println("I don't see the line");
        }
    }
}
